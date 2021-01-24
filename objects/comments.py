from .glob import glob

class AccountComment:
    """An object representation of Geometry Dash
    account comments."""

    def __init__(self):
        """Sets all default values for the object.
        Use classmethods instead."""
        
        self.id: int = -1 # -1 means not in db.
        self.account_id: int = 0 # Thought about making this an acc object but that could lead to ram issues etc.
        self.likes: int = 0
        self.content: str = "" # Plaintext content.
        self.timestamp: int = 0 # UNIX style timestamp.
    
    @classmethod
    async def from_db(cls, comment_id: int):
        """Fetches the account comment directly
        from the database and creates the
        `AccountComment` object.

        Args:
            comment_id (int): The ID of the comment
                within the database.
        
        Returns:
            None if comment not found.
            AccountComment instance if comment
                found.
        """

        # Fetch directly from db.
        comment_db = await glob.sql.fetchone("SELECT account_id, likes, content, timestamp FROM a_comments WHERE id = %s LIMIT 1", (
            comment_id,
        ))

        # Check if its found.
        if comment_db is None:
            return
        
        # Create object and fill it in.
        cls = cls()
        cls.account_id = comment_db[0]
        cls.likes = comment_db[1]
        cls.content = comment_db[2]
        cls.timestamp = comment_db[3]

        # Return it
        return cls
    
    @classmethod
    def from_tuple(cls, from_t: tuple):
        """Configures the object based on data from
        a `tuple`.
        
        Note:
            This is primarily used in database fetches
                to avoid running multiple queries.
        
        Args:
            from_t (tuple): Tuple with date in the order
                of id, account_id, likes, content, timestamp.
        """

        cls = cls()

        (
            cls.id,
            cls.account_id,
            cls.likes,
            cls.content,
            cls.timestamp
        ) = from_t

        return cls

    async def insert(self):
        """Inserts the content of the object directly
        into the MySQL database.
        
        Note:
            The check if the comment is already in the
                database is done by checking it the
                id variable is equal to its default
                value (-1)
        
        """

        if self.id != -1:
            # It already exists we think. Idk if this is the right exception.
            raise FileExistsError("This comment already exists in the database!")
        
        # Just insert it ig.
        row = await glob.sql.execute(
            "INSERT INTO a_comments (account_id, likes, content, timestamp) "
            "VALUES (%s,%s,%s,%s)",
            (self.account_id, self.likes, self.content, self.timestamp)
        )

        # Now we set the id as lastrowid.
        self.id = row
    
    async def save(self):
        """Saves the current version of the object to
        the database, replacing the current database
        entry.
        
        Note:
            For this to work, the comment must already
                be in the database. If it isn't, please
                use the `insert` coroutine.
        """

        if self.id == -1:
            # It doesnt exist to our knowledge. Idk if this is the right exception.
            raise FileNotFoundError("A comment must be inserted to the db prior to its updating.")

        # Just run the update query.
        await glob.sql.execute(
            "UPDATE a_comments SET account_id = %s, likes = %s, content = %s, "
            "timestamp = %s WHERE id = %s LIMIT 1",
            (self.account_id, self.likes, self.content, self.timestamp, self.id)
        )
