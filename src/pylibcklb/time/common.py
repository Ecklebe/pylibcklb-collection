from datetime import datetime


def get_current_utc_time_ms():
    return datetime.utcnow().isoformat(timespec='milliseconds')
