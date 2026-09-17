from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_datetime() -> dict[str, str]:
    """
    Return the current date and time in Asia/Kolkata timezone.

    Returns:
        dict[str, str]: Current date, time, and weekday.
    """

    current_datetime = datetime.now(ZoneInfo("Asia/Kolkata"))

    return {
        "current_date": current_datetime.strftime("%Y-%m-%d"),
        "current_time": current_datetime.strftime("%H:%M:%S"),
        "current_weekday": current_datetime.strftime("%A"),
    }