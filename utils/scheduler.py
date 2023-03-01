"""Tasks Scheduler"""

from functools import wraps
from uuid import uuid4
from database.models import ScheduledTask
from utils.scraping import scrape_data
from constants.app_constants import SCRAPING_SCHEDULER_DURATION


def add_task(func, job_id):
    """Decorator function to initialize scraping and save details to database"""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        task = func.delay()
        scheduled_task = ScheduledTask(
            jobId=job_id, celeryTask=task.id, description="scrape_data"
        )
        scheduled_task.save()

    return decorated_function


def init_scheduler_jobs(scheduler):
    """Initialize Scheduled Jobs"""

    job_id = str(uuid4())
    scheduler.add_job(
        id=job_id,
        func=add_task(scrape_data, job_id),
        trigger="interval",
        minutes=SCRAPING_SCHEDULER_DURATION,
    )
