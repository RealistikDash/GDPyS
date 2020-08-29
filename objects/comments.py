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
