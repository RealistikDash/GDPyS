from .user import User
from .glob import sql, level_cache

class Comment:
    """An object representation of the Geometry Dash comment meant for internal
    representation in GDPyS."""

    __slots__ = (
        "id", "poster", "level_id", "content", "timestamp", "progress", "likes"
    )

    def __init__(self) -> None:
        """Creates an instance of the class with default values. Please use
        the provided classmethods instead."""

        self.id: int = 0
        self.poster: User = User()
        self.level_id: int = 0 # We do not need to refer to an instance of level.
        self.content: str = ""
        self.timestamp: int = 0
        self.progress: int = 0 # GD thing, 0 = no progress included
        self.likes: int = 0 # Can be negative to signify dislikes
    
    @property
    def progress_included(self) -> bool:
        """Bool corresponding to whether the comment has a progress value
        attached to it."""

        return self.progress > 0
    
    @classmethod
    async def from_tuple(cls, sql_t: tuple, provide_user = None) -> 'Comment':
        """Creates an instance of `Comment` from a tuple representing SQL data
        obtained directly from an SQL query (meant for bulk instance creation
        without requiring an individual sql query per comment).
        
        Args:
            provide_user (User): Skips the potential `User.from_id` lookup
                by setting the comment's user to the value of `provide_user`,
                increasing performance for bulk instance creation.
        """

        comment = cls()

        (
            comment.id,
            user_id,
            comment.level_id,
            comment.content,
            comment.timestamp,
            comment.progress,
            comment.likes
        ) = sql_t

        # Set instance of user.
        comment.poster = await User.from_id(user_id) if not provide_user else provide_user

        return comment

    @classmethod
    async def from_sql(cls, comment_id: int) -> 'Comment':
        """Creates an instance of comment by fetching data from SQL and setting
        it for the object.
        
        Args:
            comment_id (int): The ID of the comment present within the database.
        
        Returns:
            Instance of `Comment` if row matching `comment_id` is found in the
            database. Else `None`.
        """

        comment_db = await sql.fetchone(
            "SELECT id, user_id, level_id, content, timestamp, progress, likes "
            "FROM comments WHERE id = %s LIMIT 1", (comment_id,)
        )

        if not comment_db: return

        return await Comment.from_tuple(comment_db)

    # Not sure if we will ever use this but ig its cool for plugins.
    async def update(self, content: str = None) -> None:
        """Syncronises the contents of the database with the object alongside
        setting the object's new values."""

        # There is only really one value we realistically would would want to
        # update.
        if content: self.content = content

        await sql.execute(
            "UPDATE comments SET content = %s WHERE id = %s LIMIT 1",
            (self.content, self.id,)
        )
    
    async def insert(self) -> None:
        """Inserts the comment instance into the MySQL database.
        
        Note:
            This also sets the object's id attribute, using the cursor's
                lastrowid sent by the connnector.
        """

        self.id = await sql.execute(
            "INSERT INTO comments (user_id, level_id, content, timestamp, progress, likes) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (self.poster.id, self.level_id, self.content, self.timestamp,
            self.progress, self.likes)
        )

        # If the level is already cached, we can just insert it into the
        # comments list.
        if lvl := level_cache.get(self.level_id):
            lvl.comments.insert(0, self)
