from objects.user import User
from objects.leaderboard import Leaderboard
from const import LeaderboardTypes
from web.http import Request
from objects.glob import glob

# TODO: Place in a better place.
glob.star_lb = Leaderboard(LeaderboardTypes.TOP)
glob.cp_lb = Leaderboard(LeaderboardTypes.CP)

# Local consts.
LEADERBOARDS = {
    "top": glob.star_lb,
    "creators": glob.cp_lb
}

async def get_leaderboard(req: Request, user: User) -> str:
    """Handles the `getGJScores20.php` endpoint."""

    lb_type: Leaderboard = LEADERBOARDS.get(req.post["type"], glob.star_lb)

    return "|".join([u.resp() for u in lb_type.users])
