# Helper that assists with the whole process of authentication.
from __future__ import annotations

from typing import Optional

from .cache import LRUCache
from .crypt import gjp_decode
from const import Privileges
from logger import debug
from objects.user import User


class Auth:
    """A helper that assists with the task of authenticating users. It helps
    with GJP authentication and other minor authentication related tasks."""

    def __init__(self):
        """Establishes the auth helper."""
        self._correct_gjps: LRUCache[str] = LRUCache(capacity=200)

    async def gjp_check(self, user_id: int, gjp: str) -> Optional[User]:
        """Checks if the combination of `user_id` and `gjp` matches the
        credentials of the target user.

        Note:
            Correct GJPs from this are stored within a private cache.
            Cached results stored are used within this check.

        Args:
            user_id (int): The ID of the user that you want to authenticate.
            gjp (str): The GJP encoded variant of the user's password.

        Returns:
            If the user is successfully validated, an instance of the matching
                user's `User` object is returned.

            If the user is not successfully validated, None is returned.

            If the target is not found within either medium, None is returned.
        """

        p = await User.from_id(user_id)

        if not p:
            return

        # Banned users are auto denied.
        if not p.has_privilege(Privileges.LOGIN):
            return

        # Now we check if perhaps we already cached their val.
        if cached_gjp := self._correct_gjps.get(user_id):
            if gjp == cached_gjp:
                debug(f"{p.name} authed successfully using cache hit.")
                return p

            debug(f"{p.name} failed auth using cache hit.")
            return

        # Now we compare the p_pass with bcrypt.
        if p.check_pass(gjp_decode(gjp)):
            self._correct_gjps.cache(user_id, gjp)
            debug(f"{p.name} authed successfully using direct BCrypt check.")
            return p

        return
