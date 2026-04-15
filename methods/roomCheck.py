from datetime import datetime, timedelta


def runRoomCheck(roomList, max_age_days=1):
    """Remove rooms older than the configured max age (default 24h)."""
    cutoff = datetime.today() - timedelta(days=max_age_days)
    roomList[:] = [room for room in roomList if room["created_at"] > cutoff]
