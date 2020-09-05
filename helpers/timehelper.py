import time
from datetime import datetime
import timeago

def get_timestamp() -> int:
    """Returns current timestamp as a full integer."""
    return round(time.time())

def time_ago(timestamp : int) -> str:
    """Returns a string that is timeago from now (for GD responses)."""
    raw_timeago = timeago.format(datetime.fromtimestamp(timestamp), datetime.now())
    if raw_timeago == "just now":
        return "0"
    return raw_timeago[:-4]
