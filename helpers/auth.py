# Helper that assists with the whole process of authentication.
from objects.user import User
from .cache import Cache
from .crypt import gjp_decode
from typing import Union
from logger import debug
from const import Privileges

class Auth:
    """A helper that assists with the task of authenticating users. It helps
    with GJP authentication and other minor authentication related tasks."""

    def __init__(self):
        """Establishes the auth helper."""

        # I conciously chose to cache correct GJP values. This
        # is because bcrypt (by design) is a slow algorhythm.
        # While this massively increases its safety, it also
        # means that the hashing and checking of it is
        # computationally expensive. For example, on my
        # raspberry pi, a simple 12 round bcrypt check takes
        # OVER A SECOND. This is unacceptable for a server that
        # is meant to serve many users. So I thought I could
        # cache correct bcrypt values to make it so bcrypt only
        # has to be ran once every 30 minutes per user. 
        self._correct_gjps: Cache = Cache(
            cache_length= 30
        )
    
    async def gjp_check(self, account_id: int, gjp: str) -> Union[User, None]:
        """Checks if the combination of `account_id` and `gjp` matches the
        credentials of the target user.
        
        Note:
            Correct GJPs from this are stored within a private cache.
            Cached results stored are used within this check.
        
        Args:
            account_id (int): The ID of the user that you want to authenticate.
            gjp (str): The GJP encoded variant of the user's password.
        
        Returns:
            If the user is successfully validated, an instance of the matching 
                user's `User` object is returned.
            
            If the user is not successfully validated, None is returned.
            
            If the target is not found within either medium, None is returned.
        """

        # Fetch the user directly from any available medium.
        p = await User.from_id(account_id)

        # Check if they even exist
        if not p: return
        
        # Banned users are auto denied.
        if not p.has_privilege(Privileges.LOGIN): return

        # Now we check if perhaps we already cached their val.
        if cached_gjp := self._correct_gjps.get(account_id):
            # Check if the cached gjp matches them.
            if gjp == cached_gjp:
                debug(f"{p.name} authed successfully using cache hit.")
                return p
            
            # Fail them.
            debug(f"{p.name} failed auth using cache hit.")
            return

        # Now we compare the p_pass with bcrypt.
        if p.check_pass(gjp_decode(gjp)):
            # They successfully authed. Store this bcrypt in cache for speed.
            self._correct_gjps.cache(account_id, gjp)

            # Log our success.
            debug(f"{p.name} authed successfully using direct BCrypt check.")

            # Return p obj.
            return p
        
        # They failed.
        return
