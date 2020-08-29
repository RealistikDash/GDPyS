from dataclasses import dataclass

@dataclass
class Comment():
    """The comment structure."""
    user_id : int
    level_id : int
    timestamp : int
    likes : int
    percent : int
    spam : bool
    username : str

@dataclass
class AccountComment():
    """Account comment structure."""
    user_id : int
    comment : str
    timestamp : int
    likes : int
    spam : bool
    username : str
