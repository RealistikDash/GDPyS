from .glob import glob
from .misc import RGB
from const import Privileges

class Privilege:
    """A GDPyS privilege group, representing the privileges of users (what
    they are allowed to do essentially). These are used to group people as
    well as determine what they can and can't do."""

    def __init__(self):
        """Sets out placeholders for the class. Use classmethods instead."""

        self.id: int = -1
        self.name: str = ""
        self.descritpion: str = ""
        self.privileges: Privileges = Privileges(0)
        self.colour: RGB = RGB()

    def has_privilege(self, priv: Privileges) -> bool:
        """Check if members of the privilege group have the given permisison.
        
        Args:
            priv (Privileges): An IntFlag representing the privilege to check
                for.

        Returns:
            True if has privilege, else False.
        """

        return bool(self.privileges & priv)
    
    @classmethod
    async def from_sql(cls, sql_id: int):
        """Fetches the privilege directly from the MySQL database, seaching by
        the ID of the privilege.

        Note:
            This also caches the object globally.
        
        Args:
            sql_id (int): The ID of the privilege within the database.
        
        Returns:
            Instance of `Privilege` if found in db.
            None if not found.
        """

        self = cls()

        priv_db = await glob.sql.fetchone(
            "SELECT id, name, description, privilege, rgb FROM "
            "privileges WHERE id = %s LIMIT 1",
            (sql_id,)
        )

        # Check if we found it.
        if not priv_db:
            return
        
        # Set privilege object.
        (
            self.id,
            self.name,
            self.descritpion,
            priv,
            colour
        ) = priv_db
        self.privileges = Privileges(priv)
        self.colour = RGB.from_string(colour)

        # Cache it permanently.
        glob.privileges[priv] = self

        return self
    
    @classmethod
    async def from_priv_enum(cls, enum: int):
        """Fetches the privilege directly by searching for its total
        privilege enum.
        
        Note:
            This searches through two sources (where we can possibly
            find the object), the cache (instant) and the database
            (slow as we make 2 queries).
        
        Args:
            enum (int): The privilege enum for the privilege to fetch.
        
        Returns:
            Instance of `Privilege` if found in db.
            None if not found.
        """

        # Check the cache first.
        if p := glob.privileges.get(enum):
            return p
        
        # Nope... We have to contact the db.
        # First we fetch the id.
        db_priv = await glob.sql.fetchone(
            "SELECT id FROM privileges WHERE privilege = %s LIMIT 1",
            (enum,)
        )

        # Check if it exists in db.
        if not db_priv:
            return
        
        # Rest is handled by `from_sql`
        return await cls.from_sql(db_priv[0])
