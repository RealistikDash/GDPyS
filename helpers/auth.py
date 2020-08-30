from helpers.crypthelper import compare_bcrypt, hash_bcrypt, decode_gjp
from helpers.generalhelper import dict_keys
from conn.mysql import myconn
from dataclasses import dataclass
import logging

@dataclass
class Credentials():
    bcrypt : str
    known_gjp : str #So a bcrypt check doesnt have to be ran every time. Not sure if I will keep it in final but yeah.

class AuthHelper():
    """Class responsible for managing GJP authentication."""
    def __init__(self):
        self.cached_credentials = {}
    
    async def _cache_bcrypt(self, account_id: int):
        """Caches a person's bcrypt into an object."""
        logging.debug(f"Caching bcrypt for person {account_id}")
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT password FROM accounts WHERE accountID = %s LIMIT 1", (account_id,))
            response = await mycursor.fetchone()
        assert response is not None
        self.cached_credentials[int(account_id)] = Credentials(response[0], "")#no known gjp yet
    
    async def check_gjp(self, account_id: int, gjp: str) -> bool:
        """Verifies gjp authentication."""
        account_id = int(account_id) # Making sure it's the correct type
        if not account_id in dict_keys(self.cached_credentials):
            await self._cache_bcrypt(account_id)

        if self.cached_credentials[account_id].known_gjp == gjp:
            return True
        elif self.cached_credentials[account_id].known_gjp == "":
            logging.debug("No known GJP, checking")
            if compare_bcrypt(self.cached_credentials[account_id].bcrypt, hash_bcrypt(decode_gjp(gjp))):
                self.cached_credentials[account_id].known_gjp = gjp
                return True
        return False
    
    async def check_password(self, username: str, password: str) -> bool:
        """Checks the username and password combination."""
        # No caching here as it is rarely used
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT password FROM accounts WHERE userName LIKE %s LIMIT 1", (username,))
            response = await mycursor.fetchone()
        if response is None:
            logging.debug("Didnt find user with that username")
            return False
        return compare_bcrypt(response[0], password)
        


auth = AuthHelper() #so the same class is shared across all (for the caches)
