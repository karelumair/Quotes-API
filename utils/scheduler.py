"""Tasks Scheduler"""

from uuid import uuid4
from utils.scraping import scrape_data
from constants.app_constants import SCRAPING_SCHEDULER_TIME


def init_scheduler_jobs(scheduler):
    """Initialize Scheduled Jobs"""

    scheduler.add_job(
        id=str(uuid4().hex),
        func=scrape_data.delay,
        trigger="interval",
        minutes=SCRAPING_SCHEDULER_TIME,
    )
