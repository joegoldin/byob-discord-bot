import os
import requests
from datetime import datetime

W2G_API = "https://api.w2g.tv"


def is_w2g_configured():
    """True when the W2G API key is present in the environment."""
    return bool(_api_key())


def _api_key():
    return os.getenv("W2G_API_KEY", "").strip()


def createW2gRoom(w2g_rooms, share_url=None):
    """Create a new legacy w2g.tv room and append it to `w2g_rooms`.

    If `share_url` is provided it is queued as the room's first video.
    Returns the new room URL or None on failure.
    """
    api_key = _api_key()
    if not api_key:
        return None

    body = {"w2g_api_key": api_key}
    if share_url:
        body["share"] = share_url

    try:
        resp = requests.post(f"{W2G_API}/rooms/create.json", json=body, timeout=10)
    except requests.RequestException as e:
        print(f"w2g create failed: {e}")
        return None

    if resp.status_code not in (200, 201):
        print(f"w2g create returned {resp.status_code}: {resp.text[:200]}")
        return None

    try:
        data = resp.json()
    except ValueError:
        return None

    streamkey = data.get("streamkey")
    if not streamkey:
        return None

    url = f"https://w2g.tv/rooms/{streamkey}"
    w2g_rooms.append({
        "streamkey": streamkey,
        "url": url,
        "created_at": datetime.today().replace(microsecond=0),
    })
    return url


def addToW2gRoom(streamkey, video_url):
    """Append a video to an existing w2g.tv room playlist. Returns True on success."""
    api_key = _api_key()
    if not api_key:
        return False

    try:
        resp = requests.post(
            f"{W2G_API}/rooms/{streamkey}/playlists/current/playlist_items/sync_update",
            json={
                "w2g_api_key": api_key,
                "add_items": [{"url": video_url}],
            },
            timeout=10,
        )
    except requests.RequestException as e:
        print(f"w2g add failed: {e}")
        return False

    if resp.status_code not in (200, 201, 204):
        print(f"w2g add returned {resp.status_code}: {resp.text[:200]}")
        return False

    return True
