# The GDPyS Cron Job manager.
from helpers.time import Timer
from logger import debug, info, error
import traceback
import asyncio

# Cron job imports
from .leaderboards import refresh_leaderboards
from .cache import cache_registered, cache_feature_id

JOBS = ( # All the cron coroutine functions
    refresh_leaderboards,
    cache_registered,
    cache_feature_id
)

async def cron_runner(delay: int = 1800) -> None:
    """A forever running task that runs the cron jobs every `delay` seconds.
    
    Note:
        This is mostly meant to be ran as a bg task. Avoid calling manually.

    Args:
        delay (int): The time (in seconds) between each cron run
    """

    while True:
        await run_jobs()
        await asyncio.sleep(delay)

async def run_jobs() -> None:
    """Runs all of the cron jobs."""

    # Total Timer.
    tt = Timer()
    tt.start()
    for job in JOBS:
        debug(f"Running cron job {job.__name__} ({job.__doc__})")
        t = Timer()
        t.start()
        try: await job()
        except Exception:
            e = traceback.format_exc()
            error(
                f"There has been an exception running cron job {job.__name__}"
                f"!\n{e}"
            )
        t.end()
        debug(f"Running job {job.__name__} took {t.time_str()}")
    
    info(f"Completed running {len(JOBS)} cron jobs! Took {tt.time_str()}!")
