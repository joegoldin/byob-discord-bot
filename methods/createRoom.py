import requests
from datetime import datetime


def createRoom(serverUrl, rooms):
    """Create a byob room via API. Returns the room URL string."""
    response = requests.post(f"{serverUrl}/api/rooms")

    if response.status_code in (200, 201):
        data = response.json()["data"]

        rooms.append({
            "room_id": data["room_id"],
            "api_key": data["api_key"],
            "url": data["url"],
            "created_at": datetime.today().replace(microsecond=0),
        })

        return data["url"]
    else:
        return f"Error creating room: {response.text}"
