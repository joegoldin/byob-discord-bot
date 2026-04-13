import requests


def addToQueue(serverUrl, rooms, videoUrl):
    """Add a video URL to the most recent room's queue. Returns True on success."""
    if not rooms:
        return False

    room = rooms[-1]
    response = requests.post(
        f"{serverUrl}/api/rooms/{room['room_id']}/queue",
        headers={"Authorization": f"Bearer {room['api_key']}"},
        json={"url": videoUrl, "mode": "queue"},
    )

    return response.status_code == 200
