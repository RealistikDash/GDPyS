from .glob import glob
from .user import User
from .song import Song
from config import conf
from const import Difficulty
import aiofiles
import os
import sys

# Local Consts.
MAX_CACHE_SIZE = 5000

class Level:
    """An object representing the values and qualities of
    a Geometry Dash level in code. It contains all of the
    functions and properties to work with levels."""

    def __init__(self) -> None:
        """Sets all the placeholder attributes. Use
        classmethods instead please."""

        self.id: int = 0
        self.name: str = ""
        self.creator: User = User()
        self.comments: list = [] # TODO: Correct type hints when comment object is done.
        self.description: str = ""
        self.song: Song = Song()
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

        # Special cache for small levels.
        self._cache: str = ""
    
    @property
    def path(self) -> str:
        """Returns the path to the level's local 
        location in storage."""

        path = f"{conf.dir_levels}/{self.id}"

        # Check if the level exists locally.
        if not os.path.exists(path): return

        return path
    
    @property
    def demon(self) -> bool:
        """Returns a bool of whether the level
        has a demon rating."""

        # We can just use the star rating as
        # unrated levels cant be demons.
        return self.stars == 10
    
    @property
    def auto(self) -> bool:
        """Returns a bool of whether the level
        has the auto rating."""

        # We can just use the star rating as
        # unrated levels cant be auto.
        return self.stars == 1
    
    @property
    def featured(self) -> bool:
        """Returns a bool of whether the level is
        featured."""

        return bool(self.feature_id)

    async def load(self) -> str:
        """Loads the level data directly from
        storage and returns it.
        
        Note:
            If the level is really small, it
            can be cached for s p e e d.
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
        """Writes the level string to local
        storage.
        
        Args:
            contents (str): The level string
                to be saved.
        """

        # If the level is small enough, cache it for
        # faster access later.
        if sys.getsizeof(contents) <= MAX_CACHE_SIZE:
            self._cache = contents
        
        # Write the level to storage.
        async with aiofiles.open(f"{conf.dir_levels}/{self.id}", "w+") as f:
            await f.write(contents)
