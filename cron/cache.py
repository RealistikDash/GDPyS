# Cron jobs that maintain the cache, ensuring its relatively up to date.
from helpers.user import get_user_count
from objects import glob

async def cache_registered() -> None:
    """Caches the count of registered users."""

    glob.registered_users = await get_user_count()

async def cache_feature_id() -> None:
    """Caches newest feature id (for rating speed)."""

    feaid_db = await glob.sql.fetchone(
        "SELECT featured_id FROM levels ORDER BY featured_id DESC LIMIT 1"
    )

    # No levels on the gdps
    if not feaid_db: glob.feature_id = 0
    else: glob.feature_id = feaid_db[0]

async def refresh_rank() -> None:
    """Ensures rank consistency by refreshing the ranks of ALL currently
    cached players. Kinda expensive but fits a cache up-to-dateness.
    Given enough time sometimes ranks will appear broken for players passed
    so this is kinda required."""

    for u in glob.user_cache.get_all_items():
        await u.stats.calc_rank()
