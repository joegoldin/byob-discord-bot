from datetime import datetime


def runRoomCheck(roomList):
    """Remove rooms older than 24 hours."""
    today = datetime.today()
    roomList[:] = [room for room in roomList if (today - room["created_at"]).days < 1]
