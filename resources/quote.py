from flask import Response, request
from mongoengine.errors import DoesNotExist, ValidationError
from database.models import Quote
from flask_restful import Resource
from datetime import datetime
from utils.utils import cursorToJson, objectToJson

class QuotesApi(Resource):
    def get(self) -> Response:
        tags = request.args.get("tags", None)
        if tags != None:
            tags = tags.split(",")
            pipeline = [
                {"$match": {"tags": {"$in": tags}}},
                {"$addFields": {
                    "matchedCount": {
                        "$size": {
                            "$setIntersection": [tags, "$tags"]
                        }
                    }
                }},
                {"$sort": {"matchedCount": -1}},
                {"$project": {"matchedCount": 0}}
            ]
            cursor = Quote.objects().aggregate(pipeline)
        else:
            cursor = Quote.objects()

        quotes = cursorToJson(cursor)
        return Response(quotes, mimetype="application/json", status=200)

    def post(self) -> Response:
        try:
            body = request.get_json()
            quote =  Quote(**body)
            quote.save()
            response, status = quote.to_json(), 201
        except DoesNotExist:
            response, status = objectToJson({"Error": "Author id Does Not Exist!"}), 404
        except Exception as e:
            response, status = objectToJson({"Error": str(e)}), 400

        return Response(response, mimetype="application/json", status=status)

class QuoteApi(Resource):
    def put(self, id: str) -> Response:
        try:
            body = request.get_json()
            body['updatedOn'] = datetime.utcnow()
            quote = Quote.objects.get(id=id).update(**body)
            response, status = {'id': str(id)}, 200
        except DoesNotExist:
            response, status = {"Error": "Quote with given id Does Not Exist!"}, 404
        except Exception as e:
            response, status = {"Error": str(e)}, 400

        return Response(objectToJson(response), mimetype="application/json", status=status)

    def delete(self, id: str) -> Response:
        try:
            quote = Quote.objects.get(id=id)
            quote.delete()
            response, status = "", 204
        except (DoesNotExist, ValidationError):
            response, status = objectToJson({"Error": "Quote with given id Does Not Exist!"}), 404

        return Response(response, mimetype="application/json", status=status)

    def get(self, id: str) -> Response:
        try:
            response, status = Quote.objects.get(id=id).to_json(), 200
        except (DoesNotExist, ValidationError):
            response, status = objectToJson({"Error": "Quote with given id Does Not Exist!"}), 404

        return Response(response, mimetype="application/json", status=status)
