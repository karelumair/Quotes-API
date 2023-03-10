"""Main Application"""

import logging
from flask import Flask
from flask_restful import Api
from flask_apscheduler import APScheduler
from database.db import init_db
from resources.quote import QuotesApi, QuoteApi
from resources.author import AuthorsApi, AuthorApi
from resources.scrape import ScrapeDataApi, ScrapeStatus
from resources.stats import StatsApi
from utils.logger import init_logger
from utils.celery_app import init_celery
from utils.rate_limiter import init_limiter
from services.scraper.scheduler import init_scheduler_jobs
from config import CONFIG


def create_app(context: str = "main") -> Flask:
    """Create Flask App"""

    logger = logging.getLogger("app")
    init_logger(logger)

    app = Flask(__name__)

    app.config.update(CONFIG)

    # Initialize DB
    init_db(app)

    # Initialize Celery
    init_celery(app)

    # Rate Limiter
    init_limiter(app)

    # Routes
    api = Api(app)
    api.add_resource(QuotesApi, "/quotes/")
    api.add_resource(QuoteApi, "/quotes/<quote_id>/")
    api.add_resource(AuthorsApi, "/authors/")
    api.add_resource(AuthorApi, "/authors/<author_id>/")
    api.add_resource(ScrapeDataApi, "/scrape/data/")
    api.add_resource(ScrapeStatus, "/scrape/tasks/<task_id>/")
    api.add_resource(StatsApi, "/stats/")

    # Health check
    @app.route("/health/")
    def health_check() -> dict:
        return {"status": "ok"}

    # Schedule Tasks
    if context == "main":
        scheduler = APScheduler()
        # This allows using /scheduler/ endpoint for getting information about scheduled jobs
        scheduler.api_enabled = True
        scheduler.init_app(app)

        init_scheduler_jobs(scheduler)
        scheduler.start()

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run()
