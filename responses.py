import os
from dotenv import load_dotenv

from methods.createRoom import createRoom
from methods.roomCheck import runRoomCheck
from methods.queue import addToQueue
from roomState import rooms

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

    # Help
    if lower.startswith("!help"):
        return (
            "```\n"
            "!byob [url]     Create a room (optionally with a video)\n"
            "!q <url>         Add a video to the queue (or react with 🚀)\n"
            "!byob c          Show the current room\n"
            "!byob ls         List all active rooms\n"
            "!byob set <n>    Switch to a different room\n"
            "!help            Show this help\n"
            "!ver             Show version\n"
            "\n"
            "!w2 also works as a shortcut for !byob\n"
            "```"
        )

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
