from helpers.auth import auth
from helpers.generalhelper import dict_keys
from helpers.timehelper import get_timestamp, Timer
from helpers.crypthelper import decode_base64, hash_bcrypt
from objects.accounts import Account, AccountExtras
from objects.comments import AccountComment
from conn.mysql import myconn
from constants import Permissions
import logging

class UserHelper():
    """Responsible for caching and getting user objects and other user-related actions."""
    def __init__(self):
        # Caches
        self.object_cache = {}
        self.extra_object_cache = {}
        self.accid_userid_cache = {}
        self.ranks = {}
        self.relationships = {}
        self.user_str_cache = {}
    
    async def _create_user_object(self, account_id: int) -> Account:
        """Creates a user object."""
        account_id = int(account_id)
        user_id = await self.accid_userid(account_id)
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT userName, email, registerDate, privileges, youtubeurl, twitter, twitch, frS, mS, cS FROM accounts WHERE accountID = %s LIMIT 1", (account_id,))
            account_data = await mycursor.fetchone()
            await mycursor.execute("SELECT stars,demons,icon,color1,color2,iconType, coins,userCoins,accShip,accBall,accBird,accDart,accRobot,accGlow,creatorPoints,diamonds,orbs,accSpider,accExplosion,isBanned FROM users WHERE extID = %s LIMIT 1", (account_id,))
            user_data = await mycursor.fetchone()
            await mycursor.execute("SELECT userID, userName, comment, timestamp, likes, isSpam, commentID FROM acccomments WHERE userID = %s LIMIT 1", (user_id,))
            comments = await mycursor.fetchall()
        
        acc_comments = []

        for comment in comments:
            acc_comments.append(AccountComment(comment[0], comment[2], decode_base64(comment[2]), comment[3], comment[4], bool(comment[5]), comment[1], comment[6]))
        
        return Account(
            account_data[0],
            account_data[1],
            account_id,
            user_id,
            account_data[2],
            account_data[3],
            user_data[0],
            user_data[1],
            user_data[2],
            user_data[3],
            user_data[4],
            user_data[5],
            user_data[6],
            user_data[7],
            user_data[8],
            user_data[9],
            user_data[10],
            user_data[11],
            user_data[12],
            bool(user_data[13]),
            user_data[14],
            user_data[15],
            user_data[16],
            user_data[17],
            user_data[18],
            bool(user_data[19]),
            acc_comments,
            account_data[4],
            account_data[5],
            account_data[6],
            bool(account_data[7]),
            bool(account_data[8]),
            bool(account_data[9])
        )
    
    async def _cache_aid_uid(self, account_id: int) -> None:
        """Caches an account id to user id value."""
        account_id =int(account_id)
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT userID FROM users WHERE extID = %s LIMIT 1", (account_id,))
            user_id = await mycursor.fetchone()
        assert user_id is not None
        self.accid_userid_cache[account_id] = user_id[0]
    
    async def accid_userid(self, account_id : int) -> int:
        """Returns the userID of a user with given accountID."""
        account_id = int(account_id)
        if account_id not in dict_keys(self.accid_userid_cache):
            await self._cache_aid_uid(account_id)
        return self.accid_userid_cache[account_id]
    
    async def recache_object(self, account_id: int) -> None:
        """Forces a user object to recache."""
        account_id = int(account_id)
        obj = await self._create_user_object(account_id)
        self.object_cache[account_id] = obj
    
    async def get_object(self, account_id: int) -> Account:
        """Gets user object from cache or caches and returns it."""
        account_id = int(account_id)
        if account_id not in dict_keys(self.object_cache):
            logging.debug("Object doesnt exist! Caching.")
            await self.recache_object(account_id)
        return self.object_cache[account_id]

    async def has_privilege(self, user_obj: Account, privileges: int) -> bool:
        """Checks if a user has a privilege."""
        return bool(user_obj.privileges & privileges)
    
    async def get_accountid_from_username(self, username:str) -> int:
        """Gets an account ID from username."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT accountID FROM accounts WHERE userName LIKE %s LIMIT 1", (username,))
            accountID = await mycursor.fetchone()
        return accountID[0] if accountID is not None else False
    
    async def create_user(self, username: str, password: str, email : str, ip : str = "127.0.0.1") -> None:
        """Inserts a user into db."""
        timestamp = get_timestamp()
        hashed_password = hash_bcrypt(password)
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("INSERT INTO accounts (userName, password, email, secret, saveData, registerDate, saveKey) VALUES (%s, %s, %s, '', '', %s, '')", (username, hashed_password, email, timestamp))
            await mycursor.execute("INSERT INTO users (isRegistered, extID, userName, IP) VALUES (1, %s, %s, %s)", (mycursor.lastrowid, username, ip))
            await myconn.conn.commit()
    
    async def upload_account_comment(self, comment : AccountComment) -> None:
        """Uploads an account comment."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("")
    
    async def _create_account_extra(self, account_id: int) -> AccountExtras:
        """Creates an account extra object for user."""
        async with myconn.conn.cursor() as mycursor:
            # TODO: Replace these count queries with simple len of friend request object
            await mycursor.execute("SELECT COUNT(*) FROM friendreqs WHERE toAccountID = %s AND isNew = 1", (account_id,))
            friend_reqs = await mycursor.fetchone()
            await mycursor.execute("SELECT COUNT(*) FROM messages WHERE toAccountID = %s AND isNew = 0", (account_id,))
            new_messages = await mycursor.fetchone()
            await mycursor.execute("SELECT COUNT(*) FROM friendships WHERE (person1 = %s AND isNew2 = 1) OR  (person2 = %s AND isNew1 = 1)", (account_id,account_id))
            new_friends = await mycursor.fetchone()
        return AccountExtras(
            friend_reqs[0],
            new_messages[0],
            new_friends[0],
            [],[],[] # TODO: Finish all the lists when friendship system is fully implemented.
        )
    
    async def _cache_account_extra(self, account_id: int) -> None:
        """Caches an account extra object."""
        self.extra_object_cache[account_id] = await self._create_account_extra(account_id)
    
    async def get_account_extra(self, account_id: int) -> AccountExtras:
        """Returns an account extra object for specified user."""
        account_id = int(account_id)
        if account_id not in dict_keys(self.extra_object_cache):
            await self._cache_account_extra(account_id)
        return self.extra_object_cache[account_id]
    
    def mod_badge_level(self, privileges: int) -> int:
        """Converts privileges to mod badge level."""
        if privileges & Permissions.mod_elder:
            return 2
        elif privileges & Permissions.mod_regular:
            return 1
        return 0
    
    async def cron_calc_ranks(self) -> None:
        """Calculates all ranks for users and stores them in cache.""" # I may move this to a cron category however that does not currently exist.
        timer = Timer()
        timer.start()
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT extID FROM users WHERE extID IN (SELECT accountID FROM accounts WHERE privileges & %s AND isBot = 0) ORDER BY stars DESC", (Permissions.authenticate,))
            users = await mycursor.fetchall()
        
        curr_rank = 0 # There is most likely a better way to do this but I don't know it yet
        for user in users:
            curr_rank += 1
            self.ranks[int(user[0])] = curr_rank
        timer.end()
        logging.debug(f"Rank caching took {timer.ms_return()}ms")
    
    def get_rank(self, account_id : int) -> int:
        """Gets a users rank if cached, else returns 0."""
        if account_id not in self.ranks:
            return 0
        return self.ranks[account_id]

    async def _create_user_string(self, user_id : int) -> str:
        """Creates user sting which is used in level search."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT userName, extID FROM users WHERE userID = %s LIMIT 1", (user_id,))
            user_data = await mycursor.fetchone()
        if user_data is None:
            return None
        return f"{user_id}:{user_data[0]}:{user_data[1]}"
    
    async def _cache_user_string(self, user_id : int) -> None:
        """Caches a user string."""
        self.user_str_cache[user_id] = await self._create_user_string(user_id)
    
    async def get_user_string(self, user_id : int) -> str:
        """Gets a user sting which is used in level search."""
        user_id = int(user_id)
        if user_id not in dict_keys(self.user_str_cache):
            await self._cache_user_string(user_id)
        return self.user_str_cache[user_id]

user_helper = UserHelper() # This has to be a common class.
