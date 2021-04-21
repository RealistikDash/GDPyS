from time import time
from .glob import glob
from .user import User
from .song import Song
from config import conf
from const import Difficulty
from helpers.time_helper import get_timestamp
import aiofiles
import os
import sys

# Local Consts.
MAX_CACHE_SIZE = 5000

class Level:
    """An object representing the values and qualities of a Geometry Dash
    level in code. It contains all of the functions and properties to work
    with levels."""

    def __init__(self) -> None:
        """Sets all the placeholder attributes. Use classmethods instead
        please."""

        self.id: int = 0
        self.name: str = ""
        self.creator: User = User()
        self.comments: list = [] # TODO: Correct type hints when comment object is done.
        self.description: str = ""
        self.song: Song = Song()
        self.level_version: int = 0
        # Contains batch nodes to help with rendering
        self.extra_str: str = "0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0"
        self.replay: str = ""
        self.game_version: int = 22
        self.binary_version: int = 35
        self.timestamp: int = 0

        # Some general statistics.
        self.likes: int = 0
        self.downloads: int = 0
        self.stars: int = 0
        self.difficulty: Difficulty = Difficulty.NA
        self.demon_diff: int = 0 # TODO: Demon diff enums.
        self.coins: int = 0
        self.coins_verified: bool = False
        self.requested_stars: int = 0
        self.feature_id: int = 0 # Funnily enough features are NOT bools, but rather ordered by feaid
        self.epic: bool = False
        self.ldm: bool = False
        self.objects: int = 0
        self.password: int = 0
        self.working_time: int = 0 # Time spent building the level.

        # Special cache for small levels.
        self._cache: str = ""
    
    @property
    def path(self) -> str:
        """Returns the path to the level's local location in storage."""

        path = f"{conf.dir_levels}/{self.id}"

        # Check if the level exists locally.
        if not os.path.exists(path): return

        return path
    
    @property
    def demon(self) -> bool:
        """Returns a bool of whether the level has a demon rating."""

        # We can just use the star rating as
        # unrated levels cant be demons.
        return self.stars == 10
    
    @property
    def auto(self) -> bool:
        """Returns a bool of whether the level has the auto rating."""

        # We can just use the star rating as
        # unrated levels cant be auto.
        return self.stars == 1
    
    @property
    def featured(self) -> bool:
        """Returns a bool of whether the level is featured."""

        return bool(self.feature_id)

    async def load(self) -> str:
        """Loads the level data directly from storage and returns it.
        
        Note:
            If the level is really small, it can be cached for s p e e d.
        """

        # Check cache first in case its a really small level.
        if self._cache: return self._cache

        # Nope, we have to load it from storage.
        p = self.path

        # Check if it even is locally available
        if not p: return

        # Loading directly from storage.
        async with aiofiles.open(p, "r") as f:
            contents = await f.read()
        
        # Check if the contents are below 5kb to see
        # if we can cache.
        if sys.getsizeof(contents) <= MAX_CACHE_SIZE:
            self._cache = contents
        
        # Return it
        return contents
    
    async def write(self, contents: str) -> None:
        """Writes the level string to local storage.
        
        Args:
            contents (str): The level string to be saved.
        """

        # If the level is small enough, cache it for
        # faster access later.
        if sys.getsizeof(contents) <= MAX_CACHE_SIZE:
            self._cache = contents
        
        # Write the level to storage.
        async with aiofiles.open(f"{conf.dir_levels}/{self.id}", "w+") as f:
            await f.write(contents)
    
    def cache(self) -> None:
        """Adds the current level into the global level cache."""

        glob.level_cache.cache(self.id, self)
    
    @classmethod
    async def from_sql(cls, level_id: int, full: bool = True):
        """Fetches the level data from the MySQL database and creates an
        instance of `Level`.
        
        Args:
            level_id (int): The ID of the level in the database.
            full (bool): Whether non-crucial data will be also fetched (such
                as comments).
        """

        # Create the instance of Level.
        self = cls()

        # Fetch data from MySQL
        level_db = await glob.sql.fetchone(
            "SELECT id, name, user_id, description,"
            "song_id, extra_str, replay, game_version,"
            "binary_version, timestamp, downloads, likes,"
            "stars, difficulty, demon_diff, coins, coins_verified,"
            "requested_stars, featured_id, epic, ldm,"
            "objects, password FROM levels, working_time, level_ver WHERE "
            "id = %s LIMIT 1",
            (level_id,)
        )

        # Stop an exception if level is not found.
        if level_db is None: return

        # Set simple data and store.
        (
            self.id,
            self.name,
            user_id,
            self.description,
            song_id,
            self.extra_str,
            self.replay,
            self.game_version,
            self.binary_version,
            self.timestamp,
            self.downloads,
            self.likes,
            self.stars,
            self.difficulty,
            self.demon_diff,
            self.coins,
            self.coins_verified,
            self.requested_stars,
            self.feature_id,
            self.epic,
            self.ldm,
            self.objects,
            self.password,
            self.working_time,
            self.level_version
        ) = level_db

        # GDPyS custom objects.
        self.creator = await User.from_id(user_id)
        self.song = await Song.from_id(song_id)

        if full:
            await self._fetch_comments()
    
    @classmethod
    async def from_id(cls, level_id: int):
        """Creates an instance of `Level` from data in MySQL database.
        
        Args:
            level_id (int): The ID of the level in the database.
        
        Returns:
            `None` if not found, else instance of `Level`.
        """

        # Cache can save us A LOT of time. Check it in case we already have it
        if cache_l := glob.level_cache.get(level_id): return cache_l

        # We are required to utilise the sql (slow).
        return Level.from_sql(level_id, True)
    
    @classmethod
    async def from_submit(
        self,
        account_id: int,
        name: str,
        desc: str,
        version: int
    ):
        """Creates a level object using data from level submit."""
    
    async def insert(self) -> None:
        """Inserts the level data directly into the MySQL table.
        
        Note:
            This also sets the level ID locally based on `cur.lastrowid`.
        """

        if self.id:
            raise FileExistsError(
                "Level is already uploaded (has ID assigned)."
            )

        timestamp: int = get_timestamp()
        # We are inserting into the database, and using the cur.lastrowid for
        # setting the id locally.
        self.id = await glob.sql.execute(
            "INSERT INTO levels (name, user_id, description, song_id, replay,"
            "game_version, binary_version, timestamp, coins, requested_stars,"
            "ldm, objects, password, working_time, level_ver) VALUES (%s,%s,"
            "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                self.name, self.creator.id, self.description, self.song.id,
                self.replay, self.game_version, self.binary_version, timestamp,
                self.coins, self.requested_stars, int(self.ldm), self.objects,
                self.password, self.working_time, self.level_version
            )
        )
    
    async def update(self, **kwargs) -> None:
        """Updates the level's data locally and in MySQL."""

        ...
    
    async def _fetch_comments(self):
        """Fetches level comments from the MySQL database and sets them in the
        object."""

        ...
