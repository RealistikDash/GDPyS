from const import LeaderboardTypes, Privileges
from .user import User
from .glob import glob
from copy import copy
from typing import List
from logger import debug

# Local Constants
LEADERBOARD_TYPES = {
    LeaderboardTypes.CP: "cp",
    LeaderboardTypes.TOP: "stars"
}

class Leaderboard:
    """The GDPyS in-game leaderboard containter for storing user objects in
    their ranking position."""

    def __init__(self, lb_type: LeaderboardTypes, size: int = 50) -> None:
        """Configures the leaderboard for usage as a specific leaderboard.
        
        Args:
            lb_type (LeaderboardTypes): The leaderboard type, deciding who
                goes on them and how they are ordered.
            size (int): The max size of the leaderboard.
        """

        # List of copied users in the order of their ranking.
        self.users: List[User] = []

        self._lb_type: LeaderboardTypes = lb_type
        self._size: int = size
    
    @property
    def _column(self) -> str:
        """Returns the name of the SQL column name to order by."""

        return LEADERBOARD_TYPES.get(self._lb_type)
    
    async def _get_ids(self) -> List[int]:
        """Fetches an ordered list of the IDs of the users in the leaderboard."""

        ids_db = await glob.sql.fetchall(
            f"SELECT id FROM users WHERE {self._column} > 0 AND privileges "
            f"& {int(Privileges.PUBLIC)} ORDER BY {self._column} DESC LIMIT {self._size}"
        )

        return [i[0] for i in ids_db]
    
    async def load(self) -> None:
        """Loads the leaderboard from scratch and chaches all the results.
        
        Note:
            By its very nature, this is very slow, especially near startup as
                it fetches a lot of objects.
            Object copies are created here which may not be very memory
                efficient but it stops the leaderboard order from being messed
                up by people gaining stars.
        """

        debug("Loading leaderboard...")
        # Wipe in case we are reloading.
        self.users.clear()

        people = await self._get_ids()

        # Populate with correct objs.
        for uid in people:
            self.users.append(
                copy(await User.from_id(uid))
            )
        
        debug(f"Loaded leaderboard of size {len(self.users)}!")
