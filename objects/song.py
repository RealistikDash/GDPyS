# The main purpose of this file is to contain
# the main song object.
from .glob import glob

class Song:
    """The object representation of the GDPyS
    and Geometry Dash songs."""

    def __init__(self):
        """Sets the placeholder variables. Please
        use the classmethods instead."""

        self.id: int = -1
        self.title: str = ""
        self.author_id: int = 0
        self.author_name: str = ""
        self.size: float = 0.0 # 2dp float.
        self.author_yt: str = ""
        self.url: str = ""
    
    @property
    def full_name(self) -> str:
        """Returns the name of the song in the format
        Author Name - Song Name"""

        return f"{self.author_name} - {self.title}"
    
    @classmethod
    async def from_sql(cls, song_id: int):
        """Fetches the song data directly from the MySQL
        database and sets the object data based off it.
        
        Args:
            song_id (int): The Newgrounds ID of the song
                to be fetched.
        
        Returns:
            Instance of `Song` if found.
            None if not found.
        """

        self = cls()
        # Simple MySQL query.
        song_db = await glob.sql.fetchone(
            "SELECT id, title, author_id, author_name,"
            "size, author_yt, download FROM songs WHERE "
            "id = %s LIMIT 1",
            (song_id,)
        )

        if song_db is None:
            return
        
        # Set data.
        (
            self.id,
            self.title,
            self.author_id,
            self.author_name,
            self.size,
            self.author_yt,
            self.url
        ) = song_db

        return self
    
    async def insert(self):
        """Inserts the song data from the object
        into the MySQL database."""

        # Check if we want to assign it a new ID.
        if self.id == -1:
            # This gets converted to auto increment
            self.id = None 

        # Nothing special here... We just execute
        # the MySQL query directly and fetch the
        # last row id.
        self.id = await glob.sql.execute(
            "INSERT INTO songs (id, title, author_id,"
            "author_name, size, author_yt, download) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (
                self.id,
                self.title,
                self.author_id,
                self.author_name,
                self.size,
                self.author_yt,
                self.url
            )
        )
