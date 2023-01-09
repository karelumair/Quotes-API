from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import json_util, ObjectId
from dotenv import load_dotenv, find_dotenv
import json
import os

load_dotenv(find_dotenv())

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

mongo_client = PyMongo(app)


def getJson(data):
    return json.loads(json_util.dumps(data))


@app.route("/quotes/", methods=["GET"])
def get_quotes():
    quotes_data = mongo_client.db.quotes.find()
    quotes = [quote for quote in quotes_data]   
    count = len(quotes)

    response = {
        "quotes": getJson(quotes),
        "count": count
    }

    return jsonify(response)


@app.route("/quotes/<_id>/", methods=["GET"])
def get_quote(_id):
    try:
        filter_ = {"_id": ObjectId(_id)}
        quote = mongo_client.db.quotes.find_one_or_404(filter_)
        response = {
            "quote": getJson(quote)
        }
    except Exception as e:
        response = {
            "Error": str(e)
        }

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)