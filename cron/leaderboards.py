# The GDPyS Leaderboard Refresh
from objects.glob import glob

LEADERBOARDS = (glob.star_lb, glob.cp_lb)

async def refresh_leaderboards():
    """Refreshes all of the in-game leaderboards (CP and Star)."""

    for lb in LEADERBOARDS: await lb.load()
