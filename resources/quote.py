from flask import Response, request, current_app
from mongoengine.errors import DoesNotExist, ValidationError
from database.models import Quote
from flask_restful import Resource
from datetime import datetime
from utils.utils import cursorToJson, objectToJson

class QuotesApi(Resource):
    def get(self) -> Response:
        """Get all the Quotes

        Returns:
            Response: JSON object of all the Quotes
        """
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
            current_app.logger.info(f"GET Quotes by tags {tags}")
        else:
            cursor = Quote.objects()
            current_app.logger.info(f"GET Quotes")

        quotes = cursorToJson(cursor)
        return Response(quotes, mimetype="application/json", status=200)

    def post(self) -> Response:
        """Create new Quote

        Returns:
            Response: JSON object of created Quote
        """
        try:
            body = request.get_json()
            quote =  Quote(**body)
            quote.save()
            response, status = quote.to_json(), 201
            current_app.logger.info(f"POST Quote {quote.id}")
        except DoesNotExist:
            response, status = objectToJson({"Error": "Author id Does Not Exist!"}), 404
            current_app.logger.error(f"GET Quote: Author {id} not found")
        except Exception as e:
            response, status = objectToJson({"Error": str(e)}), 400
            current_app.logger.error(f"POST Quote {str(e)}")

        return Response(response, mimetype="application/json", status=status)

class QuoteApi(Resource):
    def put(self, id: str) -> Response:
        """Update single Quote with given id

        Args:
            id (str): Quote id

        Returns:
            Response: JSON object of Quote
        """
        try:
            body = request.get_json()
            body['updatedOn'] = datetime.utcnow()
            quote = Quote.objects.get(id=id).update(**body)
            response, status = {'id': str(id)}, 200
            current_app.logger.info(f"GET Quote {id}")
        except DoesNotExist:
            response, status = {"Error": "Quote with given id Does Not Exist!"}, 404
            current_app.logger.error(f"GET Quote {id} not found")
        except Exception as e:
            response, status = {"Error": str(e)}, 400
            current_app.logger.error(f"PUT Quote {str(e)}")

        return Response(objectToJson(response), mimetype="application/json", status=status)

    def delete(self, id: str) -> Response:
        """Delete single Quote with given id

        Args:
            id (str): Quote id

        Returns:
            Response: Empty
        """
        try:
            quote = Quote.objects.get(id=id)
            quote.delete()
            response, status = "", 204
            current_app.logger.info(f"DELETE Quote {id}")
        except (DoesNotExist, ValidationError):
            response, status = objectToJson({"Error": "Quote with given id Does Not Exist!"}), 404
            current_app.logger.error(f"DELETE Quote {id} not found")

        return Response(response, mimetype="application/json", status=status)

    def get(self, id: str) -> Response:
        """Get single Quote with given id

        Args:
            id (str): Quote id

        Returns:
            Response: JSON object of Quote
        """
        try:
            response, status = Quote.objects.get(id=id).to_json(), 200
            current_app.logger.info(f"GET Quote {id}")
        except (DoesNotExist, ValidationError):
            response, status = objectToJson({"Error": "Quote with given id Does Not Exist!"}), 404
            current_app.logger.error(f"GET Quote {id} not found")

        return Response(response, mimetype="application/json", status=status)
