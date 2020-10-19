from dataclasses import dataclass


@dataclass
class Song:
    """The song object."""

    ID: int
    name: str
    author_id: int
    author_name: str
    file_size: float
    url: str
    disabled: bool
