from helpers.crypt import bcrypt_hash, bcrypt_check
from helpers.time_helper import get_timestamp
from helpers.common import safe_username
from dataclasses import dataclass
from const import ReqStats, Privileges, Regexes
from logger import debug
from .glob import glob
from .comments import AccountComment
from .privilege import Privilege
from exceptions import GDException
from typing import List
import re

@dataclass
class Stats:
    """An object representation of a user's stats, Providing
    storage and assistance for working with stats."""

    user_id: int = 0
    stars: int = 0
    diamonds: int = 0
    coins: int = 0
    u_coins: int = 0
    demons: int = 0
    cp: int = 0
    rank: int = 0

    # Icons
    colour1: int = 0
    colour2: int = 0
    icon: int = 0
    ship: int = 0
    ufo: int = 0
    wave: int = 0
    ball: int = 0
    robot: int = 0
    spider: int = 0
    explosion: int = 0
    glow: bool = False
    display_icon: int = 0

    async def calc_rank(self):
        """Calculates the leaderboards placement for the user
        using the MySQL database.
        """

        # We don't count ranks for users with 0 stars.
        if not self.stars:
            # Count how many users are ahead of us that are not banned.
            stars_db = await glob.sql.fetchone(
                "SELECT COUNT(*) FROM users WHERE stars > %s AND privileges & %s",
                (self.stars, int(Privileges.LOGIN))
            )

            self.rank = stars_db[0] + 1
    
    async def from_sql(self, full: bool = True):
        """Sets the statistics for user directly from the MySQL
        database.
        
        Args:
            full (bool): Whether extra details such as rank should
                be calculated.
        """

        # Execute the query to fetch data.
        stats_sql = await glob.sql.fetchone(
            """
            SELECT
                stars,
                diamonds,
                coins,
                ucoins,
                demons,
                cp,
                colour1,
                colour2,
                icon,
                ship,
                ufo,
                wave,
                ball,
                robot,
                spider,
                explosion,
                glow,
                display_icon
            FROM users
            WHERE
                id = %s
            LIMIT 1
            """,
            (self.user_id,)
        )

        # Now we set the data.
        (self.stars, self.diamonds,
        self.coins, self.u_coins,
        self.demons, self.cp,
        self.colour1, self.colour2,
        self.icon, self.ship,
        self.ufo, self.wave, self.ball,
        self.robot, self.spider,
        self.explosion, self.glow,
        self.display_icon) = stats_sql

        if full:
            await self.calc_rank()
    
    async def set_stats(self, **kwargs):
        """Sets the statistics for a user from kwargs provided.
        
        Note:
            This affects both the local object and the data
                stored within the MySQL database.

        Kwargs:
            stars (int): The new starcount for the user.
            diamonds (int): The new diamond count for the
                user.
            coins (int): The new golden coin count for the
                user.
            u_coins (int): The new verified user coin count
                for the user.
            demons (int): The new demon count for the user.
            cp (int): The new creator point count for the user.
            colour1 (int): The new primary colour of the user.
            colour2 (int): The new secondary colour of the user.
            icon (int): The cube icon enum for the user.
            ship (int): The ship icon enum for the user.
            ufo (int): The UFO icon enum for the user.
            wave (int): The wave icon enum for the user.
            robot (int): The robot icon enum for the user.
            ball (int): The ball icon enum for the user.
            spider (int): The spider icon enum for the user.
            explosion (int): The explosion item enum that the
                user has equipped.
            display_icon (int): The icon that will be displayed
                on the leaderboards and profile.
            glow (bool): Whether the user's icons should have
                glow around them.
        """

        # Set all values from kwargs, with old values as defaults.
        self.stars = kwargs.get("stars", self.stars)
        self.diamonds = kwargs.get("diamonds", self.diamonds)
        self.coins = kwargs.get("coins", self.coins)
        self.u_coins = kwargs.get("u_coins", self.u_coins)
        self.demons = kwargs.get("demons", self.demons)
        self.cp = kwargs.get("cp", self.cp)
        self.colour1 = kwargs.get("colour1", self.colour1)
        self.colour2 = kwargs.get("colour2", self.colour2)
        self.icon = kwargs.get("icon", self.icon)
        self.ship = kwargs.get("ship", self.ship)
        self.ufo = kwargs.get("ufo", self.ufo)
        self.wave = kwargs.get("wave", self.wave)
        self.robot = kwargs.get("robot", self.robot)
        self.ball = kwargs.get("ball", self.ball)
        self.spider = kwargs.get("spider", self.spider)
        self.explosion = kwargs.get("explosion", self.explosion)
        self.display_icon = kwargs.get("display_icon", self.display_icon)
        self.glow = kwargs.get("glow", self.glow)

        # Set all the values within the database.
        await glob.sql.execute("""
            UPDATE users SET
                stars = %s,
                diamonds = %s,
                coins = %s,
                ucoins = %s,
                demons = %s,
                cp = %s,
                colour1 = %s,
                colour2 = %s,
                icon = %s,
                ship = %s,
                ufo = %s,
                wave = %s,
                robot = %s,
                ball = %s,
                spider = %s,
                explosion = %s,
                display_icon = %s,
                glow = %s
            WHERE id = %s LIMIT 1                
        """, (
            self.stars, self.diamonds, self.coins,
            self.u_coins, self.demons, self.cp,
            self.colour1, self.colour2, self.icon,
            self.ship, self.ufo, self.wave,
            self.robot, self.ball, self.spider,
            self.explosion, self.display_icon, int(self.glow),
            self.user_id
        ))

class User:
    """The primary class for the representation of GDPyS users.
    This class allows for the OOP way of working with users.
    """

    def __init__(self):
        """Configures all placeholders for the object. Please
        use classmethods instead."""

        self.id: int = 0
        self.name: str = ""
        self.stats: Stats = Stats()
        self.registered_timestamp: int = 0
        self.privilege: Privilege = Privilege()

        # Details
        self.bcrypt_pass: str = "" # Used for auth
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
        self.account_comments: List[AccountComment] = []
    
    @property
    def safe_name(self) -> str:
        """Creates a version of `name` thats all lower case with
        spaces replaced by underscores. Made to allow quick lookups
        and safe working."""

        return safe_username(self.name)
    
    @property
    def messages_enabled(self) -> bool:
        """A property that returns a bool corresponding to whether
        they have public messages enabled."""

        return bool(self.req_states & ReqStats.MESSAGES)
    
    @property
    def comment_history_enabled(self) -> bool:
        """A property that returns a bool corresponding to whether
        the user has their comment history set to public."""

        return bool(self.req_states & ReqStats.COMMENTS)
    
    @property
    def friend_requests_enabled(self) -> bool:
        """A property that returns a bool corresponding to whether
        the user has enabled receiving friend requests from the
        general public."""

        return bool(self.req_states & ReqStats.REQUESTS)
    
    @property
    def badge_level(self) -> int:
        """Returns the badge level enum of the user."""

        # Check if they have the elder badge.
        if self.has_privilege(Privileges.ELDER_BADGE):
            return 2
        # Regular mod badge.
        elif self.has_privilege(Privileges.MOD_BADGE):
            return 1
        
        # They do not have a mod badge.
        return 0
    
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

        cls = cls()

        # Set stats id
        cls.stats.user_id = account_id

        # Set acc_id.
        cls.id = account_id

        # Basic fetch only fetches the stats.
        await cls.stats_db()

        # These are only for "extensive" or "full" fetches
        if full:
            await cls.messages_db()
            await cls.friend_reqs_db()
            await cls.friends_db()
            await cls.accomment_db()
        return cls
    
    @classmethod
    async def from_name(cls, name: str):
        """Attempts to fetch the user object from their name.
        
        Note:
            Currently, this function works by looking up the
                name within the database and then calling the
                `from_id` classmethod. While slightly slower,
                it shouldn't be too much. However, please use
                `from_id` wherever you can so less stress on
                the db.
        
        Args:
            name (str): The username of the account we will
                fetch.
        
        Returns:
            If user found, instance of the `User` object is returned.
            If not found, `None` is returned.
        """

        # Use safe_username for a quicker lookup.
        safe_uname = safe_username(name)

        # Grab id from db.
        a_id = await glob.sql.fetchone("SELECT id FROM users WHERE username_safe = %s LIMIT 1", (safe_uname,))

        # Check if they are found.
        if a_id is None:
            return
        
        # Use the from_id classmethod.
        return await cls.from_id(a_id[0])
    
    @classmethod
    async def from_id(cls, account_id: int):
        """Attempts for fetch the account with the ID of `account_id` from
        multiple sources, which are ordered from fastest to slowest.
        
        Note:
            Currently, the only two sources included are the user cache
                and MySQL.
        
        Args:
            account_id (int): The account of the user you are fetching.
        
        Returns:
            If user found, instance of the `User` object is returned.
            If not found, `None` is returned.
        """

        # First we attempt a cache hit which is the fastest by far.
        if usr := glob.user_cache.get_cache_object(account_id):
            debug(f"User {usr.name} ({account_id}) retrieved from cache.")
            return usr
        
        # Maybe not cached... Try the database.
        if usr := await cls.from_sql(account_id):
            debug(f"User {usr.name} ({account_id}) retrieved from MySQL.")

            # Add them to the cache for speed later on.
            glob.user_cache.cache_object(account_id, usr)
            return usr
        
        # They do not exist to our knowledge.
        debug(f"Unable to find user with the ID of {account_id}")
        return
    
    @classmethod
    async def register(cls, email: str, username: str, password: str):
        """Registers the user with the given credentials, adds them to
        the database and returns an instance of their User object.
        
        Note:
            Any gdpys-related error that occurs within this function
                will be raised as a `GDException` with the GD response
                error enum corresponding to the issue.
        
        Args:
            email (str): The email under which to identify the newly
                registered user.
            username (str): The name that the user will be registered
                under.
            password (str): The password under which the user will be 
                authenticated. Will be hashed with BCrypt.
        
        Returns:
            Instance of the newly registered user.
        """

        cls = cls()

        # Firstly, we set the local variables so the properties work well.
        cls.name = username
        cls.registered_timestamp = get_timestamp()
        cls.email = email

        # Now we run checks. First, check if the username exists.
        un_exists = await glob.sql.fetchone("SELECT 1 FROM users WHERE username_safe = %s LIMIT 1", (
            cls.safe_name
        ))

        # User with that username already exists in the db.
        if un_exists:
            # Raise GDException that will be directly reported to the client.
            raise GDException("-2")
        
        # Check for email.
        em_exists = await glob.sql.fetchone("SELECT 1 FROM users WHERE email = %s LIMIT 1", (
            cls.email
        ))
        if em_exists:
            # Im not sure of the proper error but an acc with that email already exists.
            raise GDException("-3")
        
        # Regex check for the email.
        if not re.search(Regexes.EMAIL, cls.email):
            raise GDException("-6")

        # Check name length
        if not (3 < len(username) < 10):
            # Im not sure of the proper error code for this but their name is too long.
            raise GDException("-9")
        
        # Check password length
        if len(password) < 6:
            raise GDException("-8")
        
        # Do this here as its slow as hell.
        cls.bcrypt_pass = bcrypt_hash(password)

        # Insert them into the db ig.
        cls.id = await glob.sql.execute("""
            INSERT INTO users
                (username, username_safe, password, timestamp, email, req_status)
            VALUES
                (%s,%s,%s,%s,%s,%s)
        """, (cls.name, cls.safe_name, cls.bcrypt_pass, cls.registered_timestamp, cls.email, int(cls.req_states)))

        # Log.
        debug(f"{cls.name} ({cls.id}) has registered!")

        # Return obj.
        return cls

    async def stats_db(self):
        """Sets the statistics for the user directly from the database.
        
        Note:
            This sets everything contained within the users table.
        """

        # I am chosing to manually select each columns in case of db order.
        db_user = await glob.sql.fetchone("""
            SELECT
                username,
                privileges,
                email,
                password,
                timestamp,
                yt_url,
                twitter_url,
                twitch_url,
                req_status
            FROM users
            WHERE
                id = %s
            LIMIT 1
        """, (self.id,))

        # Check if it is found.
        if db_user is None:
            return
        
        # Set all the variables.
        priv = 0 # Idk i got an error without it

        (self.name, priv,
        self.email, self.bcrypt_pass,
        self.registered_timestamp,
        self.youtube_url, self.twitter_url,
        self.twitch_url, req_status)  = db_user

        # Set special objects from data
        self.req_states = ReqStats(req_status)

        # Grab privilege from global priv cache.
        self.privilege = await Privilege.from_priv_enum(priv)

        # Set statistics.
        await self.stats.from_sql()
    
    async def accomment_db(self):
        """Sets and populates the account comment list
        with `AccountComment` objects of the user."""

        # Get rid of possible old comments.
        self.account_comments.clear()

        # Firstly, we will directly fetch the user's comments from db.
        acomments_db = await glob.sql.fetchall(
            "SELECT id, account_id, likes, content, timestamp FROM "
            "a_comments WHERE account_id = %s ORDER BY timestamp DESC",
            (self.id,)
        )

        # These should be already ordered, just create the objects now.
        for com in acomments_db:
            self.account_comments.append(
                AccountComment.from_tuple(com)
            )
    
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
    
    def __str__(self) -> str:
        """Returns the username of the `User` object."""

        return self.name
    
    def __repr__(self) -> str:
        """A string representation of the `User` object."""

        return f"<User {self.name} ({self.id})>"
    
    def check_pass(self, password: str) -> bool:
        """Compares the passed plaintext `password` to the
        BCrypt hashed password.
        
        Note:
            This does NOT use the GJP cache, meaning it is
                as slow as BCrypt is. Please consider this.
        
        Args:
            password (str): The plaintext version of the
                password to compare the BCrypt to.
        
        Returns:
            Bool of whether the passwords match.
        """

        return bcrypt_check(password, self.bcrypt_pass)
    
    def has_privilege(self, priv: Privileges) -> bool:
        """Check if the user has the permission `priv`.
        
        Args:
            priv (Privileges): The privilege int flag
                to check for within the user's priv
                int flag.
        
        Returns:
            Bool whether int flag is present.
        """

        if self.privilege is None:
            return False # They don't have a privilege group due to some error?
        
        return self.privilege.has_privilege(priv)
