from dataclasses import dataclass
from .levels import Level # For command context
from .accounts import Account

@dataclass
class Comment():
    """The comment structure."""
    user_id : int
    level_id : int
    comment_base64 : str
    comment : str
    timestamp : int
    likes : int
    percent : int
    spam : bool
    username : str
    comment_id : int

@dataclass
class AccountComment():
    """Account comment structure."""
    user_id : int
    comment_base64 : str
    comment : str
    timestamp : int
    likes : int
    spam : bool
    username : str
    comment_id : int

@dataclass
class CommandContext():
    level : Level
    comment : Comment
    account : Account
