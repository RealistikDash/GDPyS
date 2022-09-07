from __future__ import annotations

from const import DB_PREFIX
from const import HandlerTypes
from const import LeaderboardTypes
from objects import glob
from objects.leaderboard import Leaderboard
from objects.user import User
from web.http import Request

# TODO: Place in a better place.
glob.star_lb = Leaderboard(LeaderboardTypes.TOP)
glob.cp_lb = Leaderboard(LeaderboardTypes.CP)

# Local consts.
LEADERBOARDS = {"top": glob.star_lb, "creators": glob.cp_lb}


@glob.add_route(
    path=DB_PREFIX + "/getGJScores20.php",
    status=HandlerTypes.PLAIN_TEXT + HandlerTypes.AUTHED,
    args=("accountID", "secret", "gdw", "type"),
)
async def get_leaderboard(req: Request, user: User) -> str:
    """Handles the `getGJScores20.php` endpoint."""

    lb_type: Leaderboard = LEADERBOARDS.get(req.post["type"], glob.star_lb)

    return "|".join([u.resp() for u in lb_type.users])
