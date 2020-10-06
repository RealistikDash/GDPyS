from .rankcalc import cron_calc_ranks
from .cpcalc import cron_calc_cp
from .cachelb import cron_top_stars, cron_top_cp
from .cachempgauntlets import cron_cache_mappacks, cron_cache_gauntlets
from helpers.timehelper import Timer, time_str
import logging
import traceback
import asyncio

CRON_JOBS = [ # 
    cron_calc_ranks,
    cron_calc_cp,
    cron_top_stars,
    cron_top_cp,
    cron_cache_mappacks,
    cron_cache_gauntlets
]

async def run_cron():
    """Runs all of the cron jobs."""
    total_t = Timer()
    total_t.start()
    for job in CRON_JOBS:
        logging.debug(f"Running job {job.__name__}")
        t = Timer()
        t.start()
        try:
            await job()
        except Exception as e:
            logging.error(f"Job {job.__name__} failed with error {e}. Enable GDPyS debug mode for the full traceback.")
            logging.debug(traceback.format_exc())
        # So we dont  gett 32846238746238ms or 0.0s
        t_str = time_str(t)
        logging.info(f"Finished job {job.__name__} in {time_str}")
    
    # Don't copy paste code now watch me not follow my own advice. If I have to use this somewhere else, I will move this to timehelper.
    t_str = time_str(total_t)
    logging.info("Finished all cron jobs in " + t_str)

#async def cron_gather():
#    """An experimental way of running all of the cron jobs simultaniously async style."""
#    logging.debug(f"Queueing {len(CRON_JOBS_CORO)} cron jobs.")
#    t = Timer()
#    t.start()
#    await asyncio.gather(*CRON_JOBS_CORO)
#    #await asyncio.wait(CRON_JOBS, return_when=asyncio.FIRST_COMPLETED)
#    t_str = time_str(t)
#    logging.info(f"Finished {len(CRON_JOBS_CORO)} jobs in {t_str}")
