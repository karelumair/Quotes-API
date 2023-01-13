from flask import Flask
from flask_restful import Api
from database.db import init_db
from resources.quote import QuotesApi, QuoteApi
from resources.author import AuthorsApi, AuthorApi
from dotenv import load_dotenv, find_dotenv
import logging
import os

load_dotenv(find_dotenv())

# Logging Configuration
logging.basicConfig(filename='logs.log',
                level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')


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
