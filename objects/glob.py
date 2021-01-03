# Shared global class.
from helpers.cache import Cache

class Glob:
    """The global object shared between most
    major GDPyS systems."""

    def __init__(self):
        """Creates all the default glob variables."""

        # User cache.
        self.user_cache: Cache = Cache(
            cache_length= 20,
            cache_limit= 200
        )
