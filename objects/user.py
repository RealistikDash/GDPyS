from dataclasses import dataclass
from const import ReqStats
from .glob import glob

@dataclass
class Stats:
    """An object representation of a user's stats."""

    stars: int = 0
    diamonds: int = 0
    coins: int = 0
    u_coins: int = 0
    demons: int = 0
    cp: int = 0

class User:
    """The primary class for the representation of GDPyS users.
    This class allows for the OOP way of working with users.
    """

    def __init__(self):
        """Configures all placeholders for the object. Please
        use classmethods instead."""

        self.name: str = ""
        self.stats: Stats = Stats()

        # Details
        #self.bcrypt_pass: str = "" # Used for auth
        self.email: str = ""

        # Socials
        self.youtube_url: str = ""
        self.twitter_url: str = ""
        self.twitch_url: str = ""

        self.req_states: ReqStats = ReqStats(7) # All enabled

        # Object lists.
        self.messages: list = []
        self.friend_reqs: list = []
        self.friends: list = []
    
    @property
    def safe_name(self) -> str:
        """Creates a version of `name` thats all lower case with
        spaces replaced by underscores. Made to allow quick lookups
        and safe working."""

        return self.name.lower().replace(" ", "_")
    
    @classmethod
    async def from_sql(cls, account_id: int, full: bool = True):
        """Fetches the `User` object directly from the database, using
        the `account_id` for lookup.
        
        Args:
            account_id (int): The account id of the user to be fetched.
            full (bool): Decides whether the full profile will be fetched
                from the database of only the minimums.
        
        Returns:
            None if user is not found within the datbase.
            User object if user is found within the database.
        """

        # TODO: do this once not tired.
        await cls.stats_db(cls)
        await cls.messages_db(cls)
        await cls.friend_reqs_db(cls)
        await cls.friends_db(cls)
        return cls

    async def stats_db(self):
        """Sets the statistics for the user directly from the database."""

        # TODO: do this once not tired.
        return
    
    async def messages_db(self):
        """Sets the user messages from the database."""

        # Do like all the object creation here etc.
        # TODO: do this once not tired.
        return
    
    async def friend_reqs_db(self):
        """Sets all friend requests from db."""

        # TODO: do this once not tired.
        return
    
    async def friends_db(self):
        """Set all firends from db."""

        # TODO: do this once not tired.
        return
