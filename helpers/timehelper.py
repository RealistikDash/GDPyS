import time
from datetime import datetime
import timeago

class Timer():
    """A simple timer class."""
    def __init__(self):
        """Initialises timer for use."""
        self.start_time = 0
        self.end_time = 0
    def start(self) -> None:
        """Begins the timer."""
        self.start_time = time.time()
    def end(self) -> float:
        """Ends the timer and returns final time."""
        self.end_time = time.time()
        return self.end_time - self.start_time
    def get_difference(self) -> float:
        """Returns the difference between start and end"""
        return self.end_time - self.start_time
    def reset(self) -> None:
        """Resets the timer."""
        self.end_time = 0
        self.start_time = 0
    def ms_return(self) -> float:
        """Returns difference in 2dp ms."""
        return round((self.end_time - self.start_time)*1000, 2)

def get_timestamp() -> int:
    """Returns current timestamp as a full integer."""
    return round(time.time())

def time_ago(timestamp : int) -> str:
    """Returns a string that is timeago from now (for GD responses)."""
    raw_timeago = timeago.format(datetime.fromtimestamp(timestamp+1), datetime.now())
    return raw_timeago[:-4]

def week_ago() -> int:
    """Returns timestamp exactly week ago."""
    return get_timestamp() - 604800
