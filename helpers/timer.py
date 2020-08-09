import time

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
    def ms_return(self):
        """Returns difference in 2dp ms."""
        return round((self.end_time - self.start_time)*1000, 2)
