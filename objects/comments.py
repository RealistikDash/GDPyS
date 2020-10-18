from dataclasses import dataclass
from helpers.timehelper import get_timestamp
from .levels import Level  # For command context
from .accounts import Account


@dataclass
class Comment:
    """The comment structure."""

    user_id: int
    level_id: int
    comment_base64: str
    comment: str
    timestamp: int
    likes: int
    percent: int
    spam: bool
    username: str
    comment_id: int


@dataclass
class AccountComment:
    """Account comment structure."""

    user_id: int
    comment_base64: str
    comment: str
    timestamp: int
    likes: int
    spam: bool
    username: str
    comment_id: int


@dataclass
class CommandContext:
    level: Level
    comment: Comment
    account: Account


@dataclass
class CommentBan:
    """Comment ban dataclass."""

    account_id: int
    end_timestamp: int
    reason: str

    def rob_response(self) -> str:
        """Returns a rob-style response"""
        return f"temp_{self.end_timestamp-get_timestamp()}_{self.reason}"
