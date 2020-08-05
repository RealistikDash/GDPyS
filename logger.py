import logging
from datetime import datetime


def formatted_time(DateTimeObject=None):
    """Returns a formatted time string."""
    if DateTimeObject == None:
        DateTimeObject = datetime.now()
    return DateTimeObject.strftime("%H:%M:%S")


logging.basicConfig(format=f"[%(levelname)s] %(message)s ({formatted_time()})")
logger = logging.getLogger("GDPyS")  # init loggers
