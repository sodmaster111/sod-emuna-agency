from datetime import datetime
from zoneinfo import ZoneInfo


TZ = ZoneInfo("Asia/Jerusalem")


def is_restricted_day(config):
    today = datetime.now(TZ).date()
    if today.weekday() == 5:
        return True

    holidays = set(config.get("holidays", []))
    return today.isoformat() in holidays
