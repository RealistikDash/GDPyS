from helpers.auth import auth
from helpers.generalhelper import dict_keys, time_coro
from helpers.timehelper import get_timestamp, Timer
from helpers.crypthelper import decode_base64, hash_bcrypt, encode_base64
from helpers.lang import lang
from objects.accounts import Account, AccountExtras, FriendRequest, Message
from objects.comments import AccountComment
from conn.mysql import myconn
from constants import Permissions, Relationships
from config import user_config
from aiofile import AIOFile
from cron.rankcalc import ranks
import logging
import os
import time

class UserHelper:
    """Responsible for caching and getting user objects and other user-related actions."""

    def __init__(self):
        # Caches
        self.object_cache = {}
        self.extra_object_cache = {}
        self.accid_userid_cache = {}
        self.userid_accid_cache = {}
        self.relationships = {}
        self.user_str_cache = {}

    async def _create_user_object(self, account_id: int) -> Account:
        """Creates a user object."""
        account_id = int(account_id)
        user_id = await self.accid_userid(account_id)
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT userName, email, registerDate, privileges, youtubeurl, twitter, twitch, frS, mS, cS FROM accounts WHERE accountID = %s LIMIT 1",
                (account_id,),
            )
            account_data = await mycursor.fetchone()
            await mycursor.execute(
                "SELECT stars,demons,icon,color1,color2,iconType, coins,userCoins,accShip,accBall,accBird,accDart,accRobot,accGlow,creatorPoints,diamonds,orbs,accSpider,accExplosion,isBanned FROM users WHERE extID = %s LIMIT 1",
                (account_id,),
            )
            user_data = await mycursor.fetchone()
            await mycursor.execute(
                "SELECT userID, userName, comment, timestamp, likes, isSpam, commentID FROM acccomments WHERE userID = %s ORDER BY timestamp DESC",
                (user_id,),
            )
            comments = await mycursor.fetchall()
        acc_comments = []

        for comment in comments:
            acc_comments.append(
                AccountComment(
                    comment[0],
                    comment[2],
                    decode_base64(comment[2]),
                    comment[3],
                    comment[4],
                    bool(comment[5]),
                    comment[1],
                    comment[6],
                )
            )

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
            bool(account_data[9]),
        )

    async def _cache_aid_uid(self, account_id: int) -> None:
        """Caches an account id to user id value."""
        account_id = int(account_id)
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT userID FROM users WHERE extID = %s LIMIT 1", (account_id,)
            )
            user_id = await mycursor.fetchone()
        assert user_id is not None
        self.accid_userid_cache[account_id] = user_id[0]

    async def accid_userid(self, account_id: int) -> int:
        """Returns the userID of a user with given accountID."""
        account_id = int(account_id)
        if account_id not in dict_keys(self.accid_userid_cache):
            await self._cache_aid_uid(account_id)
        return self.accid_userid_cache[account_id]

    async def _cache_uid_aid(self, user_id: int) -> None:
        """Caches an account id to user id value."""
        user_id = int(user_id)
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT extID FROM users WHERE userID = %s LIMIT 1", (user_id,)
            )
            acc_id = await mycursor.fetchone()
        assert acc_id is not None
        self.userid_accid_cache[user_id] = acc_id[0]

    async def userid_accid(self, user_id: int) -> int:
        """Returns the accountID of a user with given userID."""
        user_id = int(user_id)
        if user_id not in dict_keys(self.userid_accid_cache):
            await self._cache_uid_aid(user_id)
        return self.userid_accid_cache[user_id]

    async def recache_object(self, account_id: int) -> None:
        """Forces a user object to recache."""
        account_id = int(account_id)
        # obj = await self._create_user_object(account_id)
        obj = await time_coro(self._create_user_object, (account_id,))
        self.object_cache[account_id] = obj

    async def get_object(self, account_id: int) -> Account:
        """Gets user object from cache or caches and returns it."""
        if account_id not in dict_keys(self.object_cache):
            logging.debug(lang.debug("obj_caching"))
            await self.recache_object(account_id)
        return self.object_cache[account_id]

    def has_privilege(self, user_obj: Account, privileges: int) -> bool:
        """Checks if a user has a privilege."""
        if privileges is None:
            return True
        return bool(user_obj.privileges & privileges)

    async def get_accountid_from_username(self, username: str) -> int:
        """Gets an account ID from username."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT accountID FROM accounts WHERE userName LIKE %s LIMIT 1",
                (username,),
            )
            accountID = await mycursor.fetchone()
        return accountID[0] if accountID is not None else False

    async def create_user(
        self, username: str, password: str, email: str, ip: str = "127.0.0.1"
    ) -> None:
        """Inserts a user into db."""
        timestamp = get_timestamp()
        hashed_password = hash_bcrypt(password)
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "INSERT INTO accounts (userName, password, email, secret, saveData, registerDate, saveKey, privileges) VALUES (%s, %s, %s, '', '', %s, '', %s)",
                (
                    username,
                    hashed_password,
                    email,
                    timestamp,
                    user_config["default_priv"],
                ),
            )
            await mycursor.execute(
                "INSERT INTO users (isRegistered, extID, userName, IP) VALUES (1, %s, %s, %s)",
                (mycursor.lastrowid, username, ip),
            )
            await myconn.conn.commit()

    async def _create_account_extra(self, account_id: int) -> AccountExtras:
        """Creates an account extra object for user."""
        async with myconn.conn.cursor() as mycursor:
            # TODO: Replace these count queries with simple len of friend request object
            await mycursor.execute(
                "SELECT COUNT(*) FROM friendreqs WHERE toAccountID = %s AND isNew = 1",
                (account_id,),
            )
            friend_reqs = await mycursor.fetchone()
            await mycursor.execute(
                "SELECT COUNT(*) FROM messages WHERE toAccountID = %s AND isNew = 0",
                (account_id,),
            )
            new_messages = await mycursor.fetchone()
            await mycursor.execute(
                "SELECT COUNT(*) FROM friendships WHERE (person1 = %s AND isNew2 = 1) OR  (person2 = %s AND isNew1 = 1)",
                (account_id, account_id),
            )
            new_friends = await mycursor.fetchone()
        return AccountExtras(
            friend_reqs[0],
            new_messages[0],
            new_friends[0],
            [],
            [],
            [],  # TODO: Finish all the lists when friendship system is fully implemented.
        )

    async def _cache_account_extra(self, account_id: int) -> None:
        """Caches an account extra object."""
        self.extra_object_cache[account_id] = await self._create_account_extra(
            account_id
        )

    async def get_account_extra(self, account_id: int) -> AccountExtras:
        """Returns an account extra object for specified user."""
        account_id = int(account_id)
        if account_id not in dict_keys(self.extra_object_cache):
            await self._cache_account_extra(account_id)
        return self.extra_object_cache[account_id]

    def mod_badge_level(self, privileges: int) -> int:
        """Converts privileges to mod badge level."""
        if privileges & Permissions.MOD_ELDER:
            return 2
        elif privileges & Permissions.MOD_REGULAR:
            return 1
        return 0

    def get_rank(self, account_id: int) -> int:
        """Gets a users rank if cached, else returns 0."""
        if account_id not in ranks:
            return 0
        return ranks[account_id]

    async def _create_user_string(self, user_id: int) -> str:
        """Creates user sting which is used in level search."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT userName, extID FROM users WHERE userID = %s LIMIT 1",
                (user_id,),
            )
            user_data = await mycursor.fetchone()
        if user_data is None:
            return None
        return f"{user_id}:{user_data[0]}:{user_data[1]}"

    async def _cache_user_string(self, user_id: int) -> None:
        """Caches a user string."""
        self.user_str_cache[user_id] = await self._create_user_string(user_id)

    async def get_user_string(self, user_id: int) -> str:
        """Gets a user sting which is used in level search."""
        user_id = int(user_id)
        if user_id not in dict_keys(self.user_str_cache):
            await self._cache_user_string(user_id)
        return self.user_str_cache[user_id]

    async def post_account_comment(
        self,
        account_id: int,
        comment: str,
        is_base64: bool = True,
        run_privilege_check: bool = True,
    ) -> bool:
        """Posts a comment to one's account."""
        if not is_base64:
            comment = encode_base64(comment)
        user = await self.get_object(int(account_id))
        timestamp = get_timestamp()

        if (
            not self.has_privilege(user, Permissions.POST_ACC_COMMENT)
            and run_privilege_check
        ):
            return False
        if user is None:
            return False

        # Inserting it into db
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "INSERT INTO acccomments (userID,userName,comment,timestamp) VALUES (%s,%s,%s,%s)",
                (user.user_id, user.username, comment, timestamp),
            )
            await myconn.conn.commit()
        # We need to re-cache the user object due to how the current system works. (Someone please remind me to change this as yes.)
        await self.recache_object(account_id)
        return True

    async def update_user_stats(self, new_obj: Account) -> None:
        """Sets user's new statistics to db (such as star count)."""
        async with myconn.conn.cursor() as mycursor:
            # TODO : Maybe some anticheat?
            await mycursor.execute(
                """UPDATE users SET
                                        stars = %s,
                                        demons = %s,
                                        icon = %s,
                                        color1 = %s,
                                        color2 = %s, #smh not colour
                                        iconType = %s,
                                        coins = %s,
                                        userCoins = %s,
                                        accShip = %s,
                                        accBall = %s,
                                        accBird = %s,
                                        accDart = %s,
                                        accRobot = %s,
                                        accGlow = %s,
                                        creatorPoints = %s,
                                        diamonds = %s,
                                        orbs = %s,
                                        accSpider = %s,
                                        accExplosion = %s
                                    WHERE
                                        extID = %s
                                        LIMIT 1""",
                (
                    new_obj.stars,
                    new_obj.demons,
                    new_obj.icon,
                    new_obj.colour1,
                    new_obj.colour2,
                    new_obj.icon_type,
                    new_obj.coins,
                    new_obj.user_coins,
                    new_obj.ship,
                    new_obj.ball,
                    new_obj.ufo,
                    new_obj.wave,
                    new_obj.robot,
                    int(new_obj.glow),
                    new_obj.cp,
                    new_obj.diamonds,
                    new_obj.orbs,
                    new_obj.spider,
                    new_obj.explosion,
                    new_obj.account_id,
                ),
            )
            await myconn.conn.commit()
        await self.recache_object(new_obj.account_id)

    async def save_user_data(self, account_id: int, save_data: str) -> None:
        """Saves/overwrites user's data."""
        # TODO : Password removal.
        async with AIOFile(user_config["save_path"] + str(account_id), "w+") as file:
            await file.write(save_data)
            await file.fsync()

    async def load_user_data(self, account_id: int) -> str:
        """Returns save data for user."""
        save_data = ""
        if os.path.exists(user_config["save_path"] + str(account_id)):
            async with AIOFile(user_config["save_path"] + str(account_id), "r") as file:
                save_data = await file.read()
        return save_data

    async def update_profile_settings(
        self,
        account_id: int,
        youtube: str,
        twitter: str,
        twitch: str,
        ms: int,
        frs: int,
        cs: int,
    ) -> None:
        """Update the user's socials stored in the database."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "UPDATE accounts SET youtubeurl = %s, twitter = %s, twitch = %s, mS = %s, frS = %s, cS = %s WHERE accountID = %s LIMIT 1",
                (youtube, twitch, twitch, ms, frs, cs, account_id),
            )
            await myconn.conn.commit()

        await self.recache_object(
            account_id
        )  # May make this func just edit the current obj

    async def give_cp(self, account_id: int, cp: int = 1):
        """Gives a user an amount of CP."""
        logging.debug(lang.debug("cp_gain", account_id, cp))
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "UPDATE users SET creatorPoints = creatorPoints + %s WHERE extID = %s LIMIT 1",
                (
                    cp,
                    account_id,
                ),
            )
            await myconn.conn.commit()
            await self.recache_object(
                account_id
            )  # May make this func just edit the current obj

    async def get_friends(self, account_id: int) -> list:
        """Returns a list of account IDs that are friends with the user."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT person1, person2 FROM friendships WHERE person1 = %s OR person2 = %s",
                (account_id, account_id),
            )
            friendships_db = await mycursor.fetchall()
        friends = []
        for friend in friendships_db:
            # Messy but it just works :tm:
            if friend[0] == account_id:
                friends.append(friend[1])
            else:
                friends.append(friend[0])
        return friends

    def _req_list_to_objects(self, requests_db: list) -> list:
        """Converts a list of db tuples in order accountID, toAccountID, comment, uploadDate, ID, isNew to requests objects."""
        requests = []

        for req in requests_db:
            requests.append(  # How to trigger people 101
                FriendRequest(
                    id=req[4],
                    account_id=req[0],
                    target_id=req[1],
                    content_base64=req[2],
                    content=decode_base64(
                        req[2]
                    ),  # To make them easier to work with outside the game.
                    timestamp=req[3],
                    new=bool(req[5]),
                )
            )

        return requests

    async def get_friend_requests_to(self, account_id: int) -> list:
        """Returns a list of friendrequest objs to account_id passed."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT accountID, toAccountID, comment, uploadDate, ID, isNew FROM friendreqs WHERE toAccountID = %s",
                (account_id,),
            )
            requests_db = await mycursor.fetchall()

        return self._req_list_to_objects(requests_db)

    async def get_friend_requests_from(self, account_id: int) -> list:
        """Returns a list of friendrequest objs from account_id passed."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT accountID, toAccountID, comment, uploadDate, ID, isNew FROM friendreqs WHERE accountID = %s",
                (account_id,),
            )
            requests_db = await mycursor.fetchall()

        return self._req_list_to_objects(requests_db)
    
    async def get_blocked(self, account_id : int) -> list:
        """Returns a list of accountIDs the user blocked."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT person2 FROM blocks WHERE person1 = %s", (account_id,))
            blocks_db = await mycursor.fetchall()
        return [i[0] for i in blocks_db]
    
    async def block_user(self, account_id : int, target_id : int) -> None:
        """Blocks the targeted user on behalf of the passed user."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("INSERT INTO blocks (person1,person2) VALUES (%s,%s)",
            (
                account_id,
                target_id
            ))
            await myconn.conn.commit()
    
    # This is SLOW... Perhaps I may look into caching this cause like 4 queries per profile is ouch.
    async def get_relationship(self, account_id : int, target_id : int) -> int:
        """[SLOW] Returns a relationship enum for a user->user relationship."""
        # It is the user himself. Avoid any extra unnecessary checks and queries.
        if account_id == target_id:
            return Relationships.NONE
        
        async with myconn.conn.cursor() as mycursor:
            # Get friendship statuses from db.
            await mycursor.execute("SELECT COUNT(*) FROM friendships WHERE (person1 = %s AND person2 = %s) OR (person1 = %s AND person2 = %s)", (
                account_id,
                target_id,
                target_id,
                account_id
            ))
            # If a friendship does exist. Messy but eh.
            if (await mycursor.fetchone())[0]:
                return Relationships.FRIENDS

            # Checking if there is a friend req.
            await mycursor.execute("SELECT accountID, toAccountID FROM friendreqs WHERE (accountID = %s OR toAccountID = %s) OR (accountID = %s OR toAccountID = %s) LIMIT 1",
            (
                account_id,
                target_id,
                target_id,
                account_id
            ))
            friend_req_db = await mycursor.fetchone()
        
        # No such thing found.
        if friend_req_db is None:
            return Relationships.NONE

        #Its coming from him
        if friend_req_db[0] == account_id:
            return Relationships.OUTGOING_REQ
        elif friend_req_db[1] == account_id:
            return Relationships.INCOMING_REQ
        else:
            return Relationships.NONE
    
    async def gdpr_delete(self, account_id : int) -> None:
        """GDPR Compliant account deletion function."""

        # Essentially, what we are going to do is nuke every sign of the user ever.
        # Firstly, we are getting rid of them from the cache.
        # TODO : Cache wipe (do once userhelper caching system is done).
        user = await self.get_object(account_id) # To get data such as the user_id
        async with myconn.conn.cursor() as mycursor:
            # NUKE THEIR ACCOUNT AND STATS.
            # List of stuf to look for and what table
            deletions = [
                # Table       x = account_id
                ("accounts", "accountID"),
                ("users", "extID"),
                ("blocks", "person1"),
                ("blocks", "person2"),
                ("friendreqs", "accountID"),
                ("friendreqs", "toAccountID"),
                ("levels", "extID"),
                ("levelscores", "accountID"),
                ("links", "accountID"),
                ("messages", "accID"),
                ("messages", "toAccountID")
            ]
            for deletion in deletions:
                await mycursor.execute(f"DELETE FROM {deletion[0]} WHERE {deletion[1]} = {account_id}")

            await mycursor.execute("DELETE FROM comments WHERE userID = %s", (user.user_id,))
        await myconn.conn.commit()
    
    async def get_messages(self, account_id : int, get_from : bool = False, page : int = 0):
        """Gets list of message objects for user"""
        offset = page * 10
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(f"SELECT userID, userName, body, subject, accID, messageID, toAccountID, timestamp, isNew FROM messages WHERE {'toAccountID' if not get_from else 'accID'} = %s LIMIT 10 OFFSET %s", (account_id, offset))
            messages_db = await mycursor.fetchall()
        
        return [
            Message(
                user_id = i[0],
                username=i[1],
                content_base64=i[2],
                subject_base64=i[3],
                account_id=i[4],
                id = i[5],
                target_id=i[6],
                timestamp=int(i[7]),
                read= i[8]
            )
            for i in messages_db
        ]
    
    async def get_message_count(self, account_id : int, get_from : bool = False) -> int:
        """Returns the number of messages a user has."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(f"SELECT COUNT(*) FROM messages WHERE {'accID' if not get_from else 'toAccountID'} = %s", (account_id,))
            return (await mycursor.fetchall())[0]
    
    async def get_message(self, message_id: int, filter: int = None) -> Message:
        """Returns a message obj from message_id.
        Params:
        message_id: The int ID of the message you are trying to fetch.
        filters: The int of account ID that the message can be send by or to. This is to prevent users from accessing others' messages."""

        async with myconn.conn.cursor() as mycursor:
            # We will do filter check
            await mycursor.execute("SELECT userID, userName, body, subject, accID, messageID, toAccountID, timestamp, isNew FROM messages WHERE messageID = %s LIMIT 1", (message_id))
            message_db = await mycursor.fetchone()
        
        # No message like that exists.
        if message_db is None:
            return None
        
        # Object creation
        obj = Message(
            user_id = message_db[0],
            username=message_db[1],
            content_base64=message_db[2],
            subject_base64=message_db[3],
            account_id=message_db[4],
            id = message_db[5],
            target_id=message_db[6],
            timestamp=int(message_db[7]),
            read= message_db[8]
        )

        # There is a filter given.
        if filter:
            if obj.account_id != filter and obj.target_id != filter:
                return None
        
        return obj
    
    async def mark_message_as_read(self, message_id: int) -> None:
        """Marks a message as read."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("UPDATE messages SET isNew = 1 WHERE messageID = %s LIMIT 1", (message_id,))
        await myconn.conn.commit()

    async def send_message(self, subject, body, fromuser, touser) -> None:
        """Posts a message to user."""
        async with myconn.conn.cursor() as mycursor:
            mycursor.execute("SELECT COUNT(*) FROM blocks WHERE person1 = %s AND person2 = %s LIMIT 1", (touser, fromuser))
            user = mycursor.fetchone()
            if user[0] > 0:
                return "-1"
            async with myconn.conn.cursor() as mycursor:
                mycursor.execute("SELECT mS, userName FROM accounts WHERE accountID = %s", (touser)) #ill also squeeze the username in here
                username = mycursor.fetchone()

        timestamp = round(time.time())
        username = username[1]
        userid = self.aid_to_uid(fromuser)

        async with myconn.conn.cursor() as mycursor:
            mycursor.execute("""INSERT INTO messages 
                                    (accID, toAccountID, userName, userID, secret, subject, body, timestamp, isNew)
                                    VALUES
                                    (%s, %s, %s, %s, %s, %s, %s, %s, 0)
                                    """,
                                    (
                                        fromuser,
                                        touser,
                                        username,
                                        userid,
                                        None,
                                        subject,
                                        body,
                                        timestamp
                                    ))
        await myconn.conn.commit()
        return "1"

    async def ban_user(self, userid: int):
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("UPDATE isBanned = 1 FROM users WHERE extID = %s")
        await myconn.conn.commit()

    async def unban_user(self, userid: int):
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("UPDATE isBanned = 0 FROM users WHERE extID = %s")
        await myconn.conn.commit()

    async def user_is_banned(self, userid: int):
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT isBanned FROM users WHERE extID = %s")
            isbanned = await mycursor.fetchone()
        return isbanned

user_helper = UserHelper()  # This has to be a common class.
