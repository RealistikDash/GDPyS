import time
from datetime import datetime
import timeago

def get_timestamp() -> int:
    """Returns current timestamp as a full integer."""
    return round(time.time())

def time_ago(timestamp : int) -> str:
    """Returns a string that is timeago from now (for GD responses)."""
    raw_timeago = timeago.format(datetime.fromtimestamp(timestamp+1), datetime.now())
    return raw_timeago[:-4]
