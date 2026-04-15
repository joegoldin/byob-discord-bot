import os
from dotenv import load_dotenv

from methods.createRoom import createRoom
from methods.roomCheck import runRoomCheck
from methods.queue import addToQueue
from methods.createOldW2g import createW2gRoom, addToW2gRoom, is_w2g_configured
from roomState import rooms, w2g_rooms

load_dotenv()
serverUrl = os.getenv("BYOB_SERVER", "https://byob.video")


def get_response(message):
    p_message = message.strip()
    lower = p_message.lower()

    # Queue: !q <link>
    if lower.startswith("!q "):
        link = p_message[3:].strip()
        if "https://" not in link and "http://" not in link:
            return f"'{link}' does not contain a link!"
        if rooms:
            success = addToQueue(serverUrl, rooms, link)
            if success:
                return f"Added to queue! :rocket:"
            else:
                return "Failed to add to queue."
        else:
            room_url = createRoom(serverUrl, rooms)
            addToQueue(serverUrl, rooms, link)
            return f"No active rooms found!\nCreated a new room: {room_url}\nAdded to queue! :rocket:"

    # Show current room: !byob c / !w2 c
    if _cmd(lower, "c"):
        if rooms:
            return f"Current room: {rooms[-1]['url']}"
        else:
            return "No rooms made! Try !byob to make a room!"

    # List rooms: !byob ls / !w2 ls
    if _cmd(lower, "ls"):
        if rooms:
            lines = ["Active rooms:"]
            for i, room in enumerate(rooms):
                suffix = " <- current" if i == len(rooms) - 1 else ""
                lines.append(f"{i + 1}. {room['url']} ({room['created_at'].strftime('%m/%d %H:%M')}){suffix}")
            return "\n".join(lines)
        else:
            return "No rooms made! Try !byob to make a room!"

    # Set active room: !byob set <n> / !w2 set <n>
    if _cmd(lower, "set"):
        try:
            # Extract number after "set"
            parts = p_message.split()
            index = int(parts[-1]) - 1
            room = rooms.pop(index)
            rooms.append(room)
            return f"Active room set to: {rooms[-1]['url']}"
        except (ValueError, IndexError):
            return "Usage: !byob set <room number>"

    # Create room: !byob [url] / !w2 [url]
    if _is_base_cmd(lower):
        url = None
        # Extract optional URL after command
        for prefix in ("!byob ", "!w2 "):
            if lower.startswith(prefix):
                rest = p_message[len(prefix):].strip()
                if rest.startswith("http"):
                    url = rest
                break

        room_url = createRoom(serverUrl, rooms)
        if url:
            addToQueue(serverUrl, rooms, url)
            return f"Room created: {room_url}\nAdded to queue! :rocket:"
        return f"Room created: {room_url}"

    # Legacy w2g.tv: !oldw2 [url]
    # Reuses the most recent tracked w2g room (up to 2 days old, see roomCheck)
    # instead of spawning a new room every call.
    if lower.startswith("!oldw2"):
        if not is_w2g_configured():
            return "Legacy w2g.tv support is not configured (set W2G_API_KEY to enable)."

        # Extract optional URL
        parts = p_message.split(maxsplit=1)
        share_url = None
        if len(parts) > 1:
            rest = parts[1].strip()
            if rest.startswith(("http://", "https://")):
                share_url = rest

        if w2g_rooms:
            current = w2g_rooms[-1]
            if share_url:
                ok = addToW2gRoom(current["streamkey"], share_url)
                if ok:
                    return f"w2g.tv room: {current['url']}\nAdded: {share_url}"
                return f"w2g.tv room: {current['url']}\n(Failed to add {share_url})"
            return f"w2g.tv room: {current['url']}"

        # No active room — create one (optionally seeded with the URL)
        new_url = createW2gRoom(w2g_rooms, share_url)
        if not new_url:
            return "Failed to create w2g.tv room."
        if share_url:
            return f"Created w2g.tv room: {new_url}\nAdded: {share_url}"
        return f"Created w2g.tv room: {new_url}"

    # Help
    if lower.startswith("!help"):
        lines = [
            "```",
            "!byob [url]      Create a room (optionally with a video)",
            "!q <url>         Add a video to the queue (or react with 🚀)",
            "!byob c          Show the current room",
            "!byob ls         List all active rooms",
            "!byob set <n>    Switch to a different room",
            "!help            Show this help",
            "!ver             Show version",
        ]
        if is_w2g_configured():
            lines.append("!oldw2 [url]     Create a legacy w2g.tv room")
        lines.append("")
        lines.append("!w2 also works as a shortcut for !byob")
        lines.append("```")
        return "\n".join(lines)

    # Version
    if lower.startswith("!ver"):
        return "byob Discord Bot v1.0.0"

    return None


def _is_base_cmd(lower):
    """Check if message is !byob or !w2 (with or without args)."""
    return lower.startswith("!byob") or lower.startswith("!w2")


def _cmd(lower, sub):
    """Check if message matches !byob <sub> or !w2 <sub>."""
    return lower.startswith(f"!byob {sub}") or lower.startswith(f"!w2 {sub}")
