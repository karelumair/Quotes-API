import logging
import os
from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv, find_dotenv
from database.db import init_db
from resources.quote import QuotesApi, QuoteApi
from resources.author import AuthorsApi, AuthorApi
from utils.logger import init_logger

load_dotenv(find_dotenv())

MONGO_URI = os.environ.get("MONGO_URI")

logger = logging.getLogger("app")
init_logger(logger)

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {"host": MONGO_URI}


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
