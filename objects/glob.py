# Shared global class. https://cdn.discordapp.com/attachments/768893339683913728/798677938932547624/1200px-Flag_of_Poland.png
from helpers.cache import Cache
from helpers.time import get_timestamp

class Glob:
    """The global object shared between most major GDPyS systems."""

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

        self.level_cache: Cache = Cache(
            cache_length= 200,
            cache_limit= 20
        )

        # All of the privileges. Using a dict as we want
        # them to never expire.
        self.privileges: dict = {}

        # Global MySQL connection.
        self.sql = None

        # I am SO SORRY for placing this here but circular imports suck.
        self.star_lb = None
        self.cp_lb = None

        # Some statistics
        self.connections_handled: int = 0
        self.startup_time: int = get_timestamp()
        self.registered_users: int = 0 # Cached in cron
        self.feature_id: int = 0 # Latest feature id (to be incremented).

# Define glob here so we can just use it.
glob = Glob()
