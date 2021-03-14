# The GDPyS Leaderboard Refresh
from objects.glob import glob

async def refresh_leaderboards():
    """Refreshes all of the in-game leaderboards (CP and Star)."""

    for lb in (glob.star_lb, glob.cp_lb):
        await lb.load()
