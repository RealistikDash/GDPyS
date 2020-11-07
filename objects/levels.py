from dataclasses import dataclass
from .misc import RGB
from config import user_config
from aiofile import AIOFile


@dataclass
class Level:
    game_version: int
    binary_version: int
    username: str
    ID: int
    name: str
    description: str
    version: int
    length: int
    track: int
    password: int
    original: bool
    two_player: bool
    song_id: int
    objects: int
    coins: int
    requested_stars: int
    string: str
    info: str
    extra: str
    stars: int
    upload_timestamp: int
    update_timestamp: int
    verified_coins: bool
    featured: bool
    epic: bool
    demon_diff: int
    user_id: int
    account_id: int
    ldm: bool
    downloads: int
    likes: int

    async def load_string(self):
        string = self.string
        if self.string is None:
            async with AIOFile(user_config["level_path"] + str(self.ID), "r") as f:
                try:
                    string = await f.read()
                except Exception:
                    string = ""
            if user_config["cache_level_strs"]:
                self.string = string
        return string


@dataclass
class SearchQuery:
    """An object that stores all the search filter data."""

    search_type: int = 0
    offset: int = 0
    order: str = "uploadDate"
    gauntlet: int = 0
    featured: bool = False
    original: bool = False
    epic: bool = False
    two_player: bool = False
    has_stars: bool = False
    no_stars: bool = True
    length: str = 0
    song: int = 0
    custom_song: int = 0
    difficulty: str = "-"
    search_query: str = ""


@dataclass
class Rating:
    """Dataclass containing information on a new rating."""

    level_id: int
    stars: int
    featured: bool
    epic: bool
    verified_coins: bool
    demon_diff: int


@dataclass
class DailyLevel:
    """Daily level dataclass"""

    ID: int
    level_id: int
    timestamp: int
    weekly: bool

@dataclass
class MapPack:
    """Map pack dataclass."""

    ID: int
    name: str
    levels: list
    stars: int
    coins: int
    difficulty: int
    colour: RGB


@dataclass
class Gauntlet:
    ID: int
    # Might make it just a list instead but /shrug
    level1_id: int
    level2_id: int
    level3_id: int
    level4_id: int
    level5_id: int

    def level_list(self) -> tuple:
        """Returns a tuple of all levels inside the gauntlet."""
        return (
            self.level1_id,
            self.level2_id,
            self.level3_id,
            self.level4_id,
            self.level5_id,
        )


@dataclass
class Score:
    """Dataclass on level scores."""

    ID: int
    account_id: int
    level_id: int
    percentage: int
    timestamp: int
    attempts: int
    coins: int
