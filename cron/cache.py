# Cron jobs that maintain the cache, ensuring its relatively up to date.
from helpers.user import get_user_count
from objects.glob import glob

async def cache_registered() -> None:
    """Caches the count of registered users."""

    glob.registered_users = await get_user_count()
