from .user import User
from .glob import sql

class Comment:
    """An object representation of the Geometry Dash comment meant for internal
    representation in GDPyS."""

    def __init__(self) -> None:
        """Creates an instance of the class with default values. Please use
        the provided classmethods instead."""

        self.id: int = 0
        self.poster: User = User()
        self.level_id: int = 0 # We do not need to refer to an instance of level.
        self.content: str = ""
        self.timestamp: int = 0
        self.progress: int = 0 # GD thing, 0 = no progress included
    
    @property
    def progress_included(self) -> bool:
        """Bool corresponding to whether the comment has a progress value
        attached to it."""

        return self.progress > 0
    
    @classmethod
    async def from_tuple(cls, sql_t: tuple) -> 'Comment':
        """Creates an instance of `Comment` from a tuple representing SQL data
        obtained directly from an SQL query (meant for bulk instance creation
        without requiring an individual sql query per comment)."""

        comment = cls()

        (
            comment.id,
            user_id,
            comment.level_id,
            comment.content,
            comment.timestamp,
            comment.progress
        ) = sql_t

        # Set instance of user.
        comment.poster = await User.from_id(user_id)

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
            "SELECT id, user_id, level_id, content, timestamp, progress "
            "FROM comments WHERE id = %s LIMIT 1", (comment_id,)
        )

        if not comment_db: return

        return Comment.from_tuple(comment_db)

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

        ...
