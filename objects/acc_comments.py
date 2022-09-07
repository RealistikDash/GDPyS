from __future__ import annotations

from . import glob
from exceptions import GDPySAlreadyExists
from exceptions import GDPySDoesntExist
from helpers.time import get_timestamp


class AccountComment:
    """An object representation of Geometry Dash
    account comments."""

    __slots__ = ("id", "user_id", "likes", "content", "timestamp")

    def __init__(self):
        """Sets all default values for the object. Use classmethods instead."""

        # 0 means not in db.
        self.id: int = 0

        # Thought about making this an acc object but that could
        # lead to ram issues etc.
        self.user_id: int = 0
        self.likes: int = 0

        # Plaintext content.
        self.content: str = ""

        # UNIX style timestamp.
        self.timestamp: int = 0

    def api(self) -> dict:
        """Converts the object into a dict (mostly for API purposes)."""

        return {
            "id": self.id,
            "likes": self.likes,
            "content": self.content,
            "timestamp": self.timestamp,
        }

    @classmethod
    async def from_db(cls, comment_id: int):
        """Fetches the account comment directly from the database and creates
        the `AccountComment` object.

        Args:
            comment_id (int): The ID of the comment within the database.

        Returns:
            None if comment not found.
            AccountComment instance if comment found.
        """

        # Fetch directly from db.
        comment_db = await glob.sql.fetchone(
            "SELECT user_id, likes, content, timestamp, "
            + "id FROM a_comments WHERE id = %s LIMIT 1",
            (comment_id,),
        )

        # Check if its found.
        if comment_db is None:
            return

        # Create object and fill it in.
        cls = cls()

        (cls.user_id, cls.likes, cls.content, cls.timestamp, cls.id) = comment_db

        # Return it
        return cls

    @classmethod
    def from_tuple(cls, from_t: tuple):
        """Configures the object based on data from a `tuple`.

        Note:
            This is primarily used in database fetches to avoid running
                multiple queries.

        Args:
            from_t (tuple): Tuple with date in the order of id, user_id,
                likes, content, timestamp.
        """

        cls = cls()

        (cls.id, cls.user_id, cls.likes, cls.content, cls.timestamp) = from_t

        return cls

    @classmethod
    def from_text(cls, user_id: int, content: str):
        """Creates a new account comment object from the `content` argument.

        Note:
            This is commonly used for the creation of new posts, and therefore
                is mostly tailored to that function.

        Args:
            user_id (int): The account ID of the user the comment should be
                assigned to.
            content (str): The plaintext contents of the account comment.
        """

        cls = cls()

        # Now we set the main details
        cls.user_id = user_id
        cls.content = content

        # And we also set the current timestamp.
        cls.timestamp = get_timestamp()

        return cls

    async def insert(self):
        """Inserts the content of the object directly into the MySQL database.

        Note:
            The check if the comment is already in the database is done by
                checking it the id variable is equal to its default value (0)

        """

        if self.id:
            # It already exists we think. Idk if this is the right exception.
            raise GDPySAlreadyExists("This comment already exists in the database!")

        # Just insert it ig.
        row = await glob.sql.execute(
            "INSERT INTO a_comments (user_id, likes, content, timestamp) "
            "VALUES (%s,%s,%s,%s)",
            (self.user_id, self.likes, self.content, self.timestamp),
        )

        # Now we set the id as lastrowid.
        self.id = row

        # If the user is already cached, append the comment to them.
        if u := glob.user_cache.get(self.user_id):
            u.account_comments.insert(0, self)

    async def save(self):
        """Saves the current version of the object to the database, replacing
        the current database entry.

        Note:
            For this to work, the comment must already be in the database. If
                it isn't, please use the `insert` coroutine.
        """

        if not self.id:
            # It doesnt exist to our knowledge. Idk if this is the right exception.
            raise GDPySDoesntExist(
                "A comment must be inserted to the db prior to its updating.",
            )

        # Just run the update query.
        await glob.sql.execute(
            "UPDATE a_comments SET user_id = %s, likes = %s, content = %s, "
            "timestamp = %s WHERE id = %s LIMIT 1",
            (self.user_id, self.likes, self.content, self.timestamp, self.id),
        )

        # If the user is already cached, update their
        # comments. This is necessary as there isnt a
        # global acc comment cache *yet*.
        if u := glob.user_cache.get(self.user_id):
            # Look for a comment with the matching id.
            for enu, com in enumerate(u.account_comments):
                if com.id == self.id:
                    u.account_comments[enu] = self
                    break

    async def delete(self):
        """Deletes the account comment from the database and cached user."""

        if not self.id:
            # It doesnt exist to our knowledge. Idk if this is the right exception.
            raise GDPySDoesntExist(
                "A comment must be inserted to the db prior to its deletion.",
            )

        # Delete it straight from the database.
        await glob.sql.execute(
            "DELETE FROM a_comments WHERE id = %s LIMIT 1",
            (self.id,),
        )

        # Delete it from the user's cached objects list IF it is cached.
        if u := glob.user_cache.get(self.user_id):
            # We cant do account_comments.remove as we are expecting this
            # object to be different from the one in the list.
            for com in u.account_comments:
                if com.id == self.id:
                    u.account_comments.remove(com)
                    break

        self.id = 0  # Set it to 0 to signify not being in db
