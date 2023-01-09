from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import json_util
from dotenv import load_dotenv, find_dotenv
import json
import os

load_dotenv(find_dotenv())

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

mongo_client = PyMongo(app)


def getJson(data):
    return json.loads(json_util.dumps(data))


@app.route("/quotes/")
def get_quotes():
    quotes_data = mongo_client.db.quotes.find()
    quotes = [quote for quote in quotes_data]   
    count = len(quotes)

    response = {
        "quotes": getJson(quotes),
        "count": count
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)