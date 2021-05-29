# For now this is simply taken from GDPyS v2 as this has no huge flaws with it.
import time
from datetime import datetime

class Timer:
    """A simple timer class used to time the execution of code."""

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
        return round((self.end_time - self.start_time) * 1000, 2)
    
    def time_str(self) -> str:
        """Returns a nicely formatted timing result."""

        # This function already takes a timer so its a match in heaven lmfao.
        return time_str(self)


def get_timestamp() -> int:
    """Returns current timestamp as a full integer."""
    return int(time.time())


def time_ago(timestamp: int, is_ts: bool = True) -> str:
    """Returns a string that is timeago from now (for GD responses).
    
    Args:
        timestamp (int): A UNIX timestamp you want the `time_ago` string from
            if `is_ts` is not passed. Else time diff.
        is_ts (bool): Whether the timestamp passed is an actual timestamp or a
            time diff.
    """
    
    if is_ts: time_diff = get_timestamp() - int(timestamp)
    else: time_diff = timestamp

    # No difference.
    if time_diff == 0:
        return "just"
    
    # Make a non-negative variant for formatting.
    pos_diff = (time_diff if time_diff > 0 else time_diff * -1) * 60

    intervals = (
        ("second", 60), ("minute", 60), ("hour", 60), ("day", 24),
        ("months", 30), ("years", 12), ("decade", 100)
    )

    ret = ""
    for idx, time_i in enumerate(intervals):
        singular, time = time_i
        pos_diff //= time
        if pos_diff < intervals[idx + 1][1]:
            return f"{pos_diff} {singular}" + ("s" if pos_diff > 1 else "")

def week_ago() -> int:
    """Returns timestamp exactly week ago."""
    return get_timestamp() - 604800


def tomorrow() -> int:
    """Returns the timestamp of midnight tomorrow."""
    return (
        (get_timestamp() // 86400) * 86400
    ) + 86400  # SMARTEST PROGRAMMER THAT HAS EVER LIVED


def time_since_midnight() -> int:
    """Returns time since midnight."""
    now = datetime.now()
    return round(
        (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    )


def time_str(timer: Timer) -> str:
    """If time is in ms, returns ms value. Else returns rounded seconds value."""
    time = timer.end()
    if time < 1:
        time_str = f"{timer.ms_return()}ms"
    else:
        time_str = f"{round(time,2)}s"
    return time_str

def formatted_date():
    """Returns the current fromatted date in the format
    DD/MM/YYYY HH:MM:SS"""
    
    return time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
