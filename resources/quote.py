from flask import Response, request
from database.models import Quote
from flask_restful import Resource
from datetime import datetime
from utils.utils import cursorToJson

class QuotesApi(Resource):
    def get(self):
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
            quotes = cursorToJson(cursor)
        else:
            quotes = Quote.objects().to_json()
        return Response(quotes, mimetype="application/json", status=200)

    def post(self):
        body = request.get_json()
        quote =  Quote(**body).save().to_json()
        return Response(quote, mimetype="application/json", status=200)
        
class QuoteApi(Resource):
    def put(self, id):
        body = request.get_json()
        body['updatedOn'] = datetime.utcnow()
        quote = Quote.objects.get(id=id).update(**body)
        return {'id': str(id)}, 200
    
    def delete(self, id):
        quote = Quote.objects.get(id=id).delete()
        return '', 200

    def get(self, id):
        quotes = Quote.objects.get(id=id).to_json()
        return Response(quotes, mimetype="application/json", status=200)