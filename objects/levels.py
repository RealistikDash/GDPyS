from dataclasses import dataclass

@dataclass
class Level():
    game_version : int
    level_id : int
    name : str
    description : str
    version : int
