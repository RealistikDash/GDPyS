#simple misc functions thaat aim to replace 
import time

def dict_keys(dictioary: dict) -> tuple:
    """Returns a tuple of all the dictionary keys."""
    return tuple(dictioary.keys())

def timestamp() -> int:
    """Gets current timestamp as an int."""
    return round(time.time())
