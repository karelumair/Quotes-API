"""Main Application"""

import logging
import os
from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv, find_dotenv
from database.db import init_db
from resources.error_handler import bad_request, error_handler_blueprint
from resources.quote import QuotesApi, QuoteApi
from resources.author import AuthorsApi, AuthorApi
from resources.scrape import ScrapeQuotesApi, ScrapeAuthorsApi, ScrapeStatus
from utils.logger import init_logger
from utils.celery_app import init_celery

load_dotenv(find_dotenv())

MONGO_URI = os.environ.get("MONGO_URI")
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")

logger = logging.getLogger("app")
init_logger(logger)

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {"host": MONGO_URI}
app.config.from_mapping(
    CELERY={
        "broker_url": "redis://localhost",
        "result_backend": "redis://localhost",
    }
)


# Initialize DB
init_db(app)

# Initialize Celery
celery = init_celery(app)

# Routes
api = Api(app)
api.add_resource(QuotesApi, "/quotes/")
api.add_resource(QuoteApi, "/quotes/<quote_id>/")
api.add_resource(AuthorsApi, "/authors/")
api.add_resource(AuthorApi, "/authors/<author_id>/")
api.add_resource(ScrapeQuotesApi, "/scrape/quotes/")
api.add_resource(ScrapeAuthorsApi, "/scrape/authors/")
api.add_resource(ScrapeStatus, "/scrape/tasks/<task_id>/")

# Error Handlers
app.register_blueprint(error_handler_blueprint)
app.register_error_handler(400, bad_request)

if __name__ == "__main__":
    app.run(debug=True)
