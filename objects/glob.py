# Shared global class. https://cdn.discordapp.com/attachments/768893339683913728/798677938932547624/1200px-Flag_of_Poland.png
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
        # Song Cache
        self.song_cache: Cache = Cache(
            cache_length= 20,
            cache_limit= 200
        )

        # All of the privileges. Using a dict as we want
        # them to never expire.
        self.privileges: dict = {}

        # Global MySQL connection.
        self.sql = None

# Define glob here so we can just use it.
glob = Glob()
