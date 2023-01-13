from flask import Flask
from flask_restful import Api
from database.db import init_db
from resources.quote import QuotesApi, QuoteApi
from resources.author import AuthorsApi, AuthorApi
from dotenv import load_dotenv, find_dotenv
from utils.logging import init_logger
import logging
import os

load_dotenv(find_dotenv())

logger = logging.getLogger("app")
init_logger(logger)

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {
    "host": os.environ.get("MONGO_URI")
}


# Initialize DB
init_db(app)


# Routes
api = Api(app)
api.add_resource(QuotesApi, "/quotes/")
api.add_resource(QuoteApi, "/quotes/<id>/")
api.add_resource(AuthorsApi, "/authors/")
api.add_resource(AuthorApi, "/authors/<id>/")


if __name__ == "__main__":
    app.run(debug=True)
