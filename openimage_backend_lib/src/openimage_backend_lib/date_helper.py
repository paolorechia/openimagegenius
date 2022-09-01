from datetime import datetime, timezone


def get_iso_and_timestamp_now():
    creation_time = datetime.now(tz=timezone.utc)
    creation_time_iso = creation_time.isoformat()
    creation_time_timestamp = creation_time.timestamp()
    return str(creation_time_iso), str(creation_time_timestamp)
