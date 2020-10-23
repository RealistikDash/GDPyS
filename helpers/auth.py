from helpers.crypthelper import compare_bcrypt, decode_gjp
from helpers.generalhelper import dict_keys
from helpers.lang import lang
from .cache import Cache
from conn.mysql import myconn
from dataclasses import dataclass
import logging


@dataclass
class Credentials:
    bcrypt: str
    known_gjp: str  # So a bcrypt check doesnt have to be ran every time. Not sure if I will keep it in final but yeah.


class AuthHelper:
    """Class responsible for managing GJP authentication."""

    def __init__(self):
        self.cache = Cache(
            cache_length=60,
            cache_limit=500
        )

    async def _cache_bcrypt(self, account_id: int) -> Credentials:
        """Caches a person's bcrypt into an object."""
        logging.debug(lang.debug("cache_bcrypt", account_id))
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT password FROM accounts WHERE accountID = %s LIMIT 1",
                (account_id,),
            )
            response = await mycursor.fetchone()
        assert response is not None
        credential = Credentials(
            response[0], ""
        )  # no known gjp yet
        self.cache.cache_object(int(account_id),credential)
        return credential

    async def check_gjp(self, account_id: int, gjp: str) -> bool:
        """Verifies gjp authentication."""
        account_id = int(account_id)  # Making sure it's the correct type
        credential = self.cache.get_cache_object(account_id) 
        if credential is None:
            credential = await self._cache_bcrypt(account_id)

        if credential.known_gjp == gjp:
            return True
        elif credential.known_gjp == "": # No GJP cached yet.
            logging.debug(lang.debug("no_gjp"))
            if compare_bcrypt(
                decode_gjp(gjp), credential.bcrypt
            ):
                credential.known_gjp = gjp
                # Overwrite cached gjp
                self.cache.remove_cache_object(account_id)
                self.cache.cache_object(account_id, credential)
                return True
        logging.debug(lang.debug("bcrypt_fail"))
        return False

    async def check_password(self, username: str, password: str) -> bool:
        """Checks the username and password combination."""
        # No caching here as it is rarely used
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute(
                "SELECT password FROM accounts WHERE userName LIKE %s LIMIT 1",
                (username,),
            )
            response = await mycursor.fetchone()
        if response is None:
            logging.debug(lang.debug("user_not_found"))
            return False
        return compare_bcrypt(password, response[0])


auth = AuthHelper()  # so the same class is shared across all (for the caches)
