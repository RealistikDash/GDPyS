from dataclasses import dataclass

@dataclass
class Level():
    game_version : int
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
    string : str
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

@dataclass
class SearchQuery():
    """An object that stores all the search filter data."""
    search_type : int
    offset : int
    order : str
    gauntlet : int
    featured : bool
    original : bool
    epic : bool
    two_player : bool
    has_stars : bool
    no_stars : bool
    length : str
    song : int
    custom_song : int
    difficulty : str
    search_query : str
