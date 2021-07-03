from .user import User

class Comment:
    """An object representation of the Geometry Dash comment meant for internal
    representation in GDPyS."""

    def __init__(self) -> None:
        """Creates an instance of the class with default values. Please use
        the provided classmethods instead."""

        self.id: int = 0
        self.poster: User = User()
        self.content: str = ""
        self.timestamp: int = 0
        self.progress: int = 0 # GD thing, 0 = no progress included
