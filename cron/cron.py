from .rankcalc import cron_calc_ranks
from .cpcalc import cron_calc_cp
from helpers.timehelper import Timer
import logging
import traceback

CRON_JOBS = [ # 
    cron_calc_ranks,
    cron_calc_cp
]

async def run_cron():
    """Runs all of the cron jobs."""
    for job in CRON_JOBS:
        logging.debug(f"Running job {job.__name__}")
        t = Timer()
        t.start()
        try:
            await job()
        except Exception as e:
            logging.error(f"Job {job.__name__} failed with error {e}. Enable GDPyS debug mode for the full traceback.")
            logging.debug(traceback.format_exc())
        time = t.end()
        # So we dont  gett 32846238746238ms or 0.0s
        if time < 1:
            time_str = f"{t.ms_return()}ms"
        else:
            time_str = f"{round(time,2)}s"
        logging.info(f"Finished job {job.__name__} in {time_str}")
