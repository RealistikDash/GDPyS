from objects.user import User
from objects.leaderboard import Leaderboard
from const import LeaderboardTypes
from web.http import Request

# TODO: Place in a better place.
top_lb: Leaderboard = Leaderboard(LeaderboardTypes.TOP)
cp_lb: Leaderboard = Leaderboard(LeaderboardTypes.CP)

async def get_leaderboard(req: Request, user: User) -> str:
    """Handles the `getGJScores20.php` endpoint."""

    lb_type: Leaderboard = {
        "top": top_lb,
        "creators": cp_lb
    }.get(req.post["type"], top_lb)

    # Check whether to load them from scratch. TODO: Rearrange this.
    if not lb_type.users:
        await lb_type.load()

    return "|".join([u.resp() for u in lb_type.users])
