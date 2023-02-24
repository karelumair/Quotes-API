"""Main Application"""

import logging
from flask import Flask
from flask_restful import Api
from database.db import init_db
from resources.error_handler import bad_request, error_handler_blueprint
from resources.quote import QuotesApi, QuoteApi
from resources.author import AuthorsApi, AuthorApi
from resources.scrape import ScrapeQuotesApi, ScrapeAuthorsApi, ScrapeStatus
from utils.logger import init_logger
from utils.celery_app import init_celery
from config import CONFIG


def create_app(env: str = "test") -> Flask:
    """Create Flask App"""

    logger = logging.getLogger("app")
    init_logger(logger)

    app = Flask(__name__)

    if env == "test":
        app.config.update(CONFIG["test"])
    else:
        app.config.update(CONFIG["prod"])

    # Initialize DB
    init_db(app)

    # Initialize Celery
    init_celery(app)

    # Routes
    api = Api(app)
    api.add_resource(QuotesApi, "/quotes/")
    api.add_resource(QuoteApi, "/quotes/<quote_id>/")
    api.add_resource(AuthorsApi, "/authors/")
    api.add_resource(AuthorApi, "/authors/<author_id>/")
    api.add_resource(ScrapeQuotesApi, "/scrape/quotes/")
    api.add_resource(ScrapeAuthorsApi, "/scrape/authors/")
    api.add_resource(ScrapeStatus, "/scrape/tasks/<task_id>/")

    # Health check
    @app.route("/health/")
    def health_check():
        return {"status": "ok"}

    # Error Handlers
    app.register_blueprint(error_handler_blueprint)
    app.register_error_handler(400, bad_request)

    return app


if __name__ == "__main__":
    flask_app = create_app(env="prod")
    flask_app.run(debug=True)
