"""Scraping Tasks Scheduler"""

from typing import Callable
from functools import wraps
from uuid import uuid4
from flask_apscheduler import APScheduler
from database.models import ScheduledTask
from services.scraper.scraper import scrape_data_scheduler
from constants.app_constants import SCRAPING_SCHEDULER_DURATION


def add_task(func: Callable, job_id: str) -> Callable:
    """Decorator function to initialize scraping and save details to database"""

    @wraps(func)
    def decorated_function(*args, **kwargs):  # pylint: disable=W0613
        scheduled_task = ScheduledTask(jobId=job_id, description="scrape_data")
        scheduled_task.save()
        func.delay(task_id=str(scheduled_task.id))

    return decorated_function


def init_scheduler_jobs(scheduler: APScheduler) -> None:
    """Initialize Scheduled Jobs"""

    job_id = str(uuid4())
    scheduler.add_job(
        id=job_id,
        func=add_task(scrape_data_scheduler, job_id),
        trigger="interval",
        minutes=SCRAPING_SCHEDULER_DURATION,
    )
