from dataclasses import dataclass
from config import user_config

@dataclass
class Level():
    game_version : int
    binary_version : int
    username : str
    ID : int
    name : str
    description : str
    version : int
    length : int
    track : int
    password : int
    original : bool
    two_player : bool
    song_id : bool
    objects : int
    coins : int
    requested_stars : int
    string : str = None
    info : str
    extra : str
    stars : int
    upload_timestamp : int
    update_timestamp : int
    verified_coins : bool
    featured: bool
    epic : bool
    demon_diff : int
    user_id : int
    account_id : int
    ldm : bool

    def load_string(self):
        if self.string is None:
            with open(user_config["level_path"] + str(self.ID), "r") as f:
                try:
                    self.string = f.readlines()[0]
                except Exception:
                    self.string = ""
        return self.string

@dataclass
class SearchQuery():
    """An object that stores all the search filter data."""
    search_type : int = 0
    offset : int = 0
    order : str = "uploadDate"
    gauntlet : int = 0
    featured : bool = False
    original : bool = False
    epic : bool = False
    two_player : bool = False
    has_stars : bool = False
    no_stars : bool = True
    length : str = 0
    song : int = 0
    custom_song : int = 0
    difficulty : str = "-"
    search_query : str = ""
