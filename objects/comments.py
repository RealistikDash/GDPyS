class Comment():
    """The comment structure"""
    def __init__(self, user_id: int = None, username: str = None, level_id: int = None, timestamp: int = None, likes: int = None, percent: int = None, spam: bool = None):
        """Creates the comment object."""
        self.user_id = user_id
        self.username = username
        self.level_id = level_id
        self.timestamp = timestamp
        self.likes = likes
        self.percent = percent
        self.spam = spam