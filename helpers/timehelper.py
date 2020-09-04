import time

def get_timestamp() -> int:
    """Returns current timestamp as a full integer."""
    return round(time.time())
