"""All the Quotes API endpoints"""

from datetime import datetime, timezone
from flask import Response, request, jsonify, make_response, current_app
from mongoengine.errors import DoesNotExist, ValidationError
from flask_restful import Resource
from database.models import Quote
from database.schemas import QuoteSchema, QuoteUpdateSchema
from utils.utils import cursor_to_json


class QuotesApi(Resource):
    """GET and POST API for Quotes"""

    def get(self) -> Response:
        """Get all the Quotes

        Returns:
            Response: JSON object of all the Quotes
        """
        tags = request.args.get("tags", None)
        if tags is not None:
            tags = tags.split(",")
            pipeline = [
                {"$match": {"tags": {"$in": tags}}},
                {
                    "$addFields": {
                        "matchedCount": {"$size": {"$setIntersection": [tags, "$tags"]}}
                    }
                },
                {"$sort": {"matchedCount": -1}},
                {"$project": {"matchedCount": 0}},
            ]
            cursor = Quote.objects().aggregate(pipeline)
            current_app.logger.info(f"GET Quotes by tags {tags}")
        else:
            cursor = Quote.objects(author__exists=True).exclude("scrapedAuthor")
            current_app.logger.info("GET Quotes")

        quotes = cursor_to_json(cursor)
        return make_response(jsonify(quotes), 200)

    def post(self) -> Response:
        """Create new Quote

        Returns:
            Response: JSON object of created Quote
        """
        try:
            body = request.get_json()

            quote_validate = QuoteSchema(**body)
            quote = Quote(**quote_validate.dict())
            quote.save()

            response, status = quote.to_json(), 201
            current_app.logger.info(f"POST Quote {quote.id}")
        except DoesNotExist:
            response, status = {"Error": "Author id Does Not Exist!"}, 404
            current_app.logger.error("GET Quote: Author not found")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"POST Quote {str(exp_err)}")

        return make_response(jsonify(response), status)


class QuoteApi(Resource):
    """GET Detail, PUT, and DELETE API for Quotes"""

    def put(self, quote_id: str) -> Response:
        """Update single Quote with given id

        Args:
            id (str): Quote id

        Returns:
            Response: JSON object of Quote
        """
        try:
            body = request.get_json()
            body["updatedOn"] = datetime.now(timezone.utc)

            quote_validate = QuoteUpdateSchema(**body)
            update_values = {
                k: v for k, v in quote_validate.dict().items() if v is not None
            }
            Quote.objects.get(id=quote_id).update(**update_values)

            response, status = {"id": quote_id}, 200
            current_app.logger.info(f"GET Quote {quote_id}")
        except DoesNotExist:
            response, status = {"Error": "Quote with given id Does Not Exist!"}, 404
            current_app.logger.error(f"GET Quote {quote_id} not found")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"PUT Quote {str(exp_err)}")

        return make_response(jsonify(response), status)

    def delete(self, quote_id: str) -> Response:
        """Delete single Quote with given id

        Args:
            id (str): Quote id

        Returns:
            Response: Empty
        """
        try:
            quote = Quote.objects.get(id=quote_id)
            quote.delete()
            response, status = "", 204
            current_app.logger.info(f"DELETE Quote {quote_id}")
        except (DoesNotExist, ValidationError):
            response, status = {"Error": "Quote with given id Does Not Exist!"}, 404
            current_app.logger.error(f"DELETE Quote {quote_id} not found")

        return make_response(jsonify(response), status)

    def get(self, quote_id: str) -> Response:
        """Get single Quote with given id

        Args:
            id (str): Quote id

        Returns:
            Response: JSON object of Quote
        """
        try:
            response, status = Quote.objects.get(id=quote_id).to_json(), 200
            current_app.logger.info(f"GET Quote {quote_id}")
        except (DoesNotExist, ValidationError):
            response, status = {"Error": "Quote with given id Does Not Exist!"}, 404
            current_app.logger.error(f"GET Quote {quote_id} not found")

        return make_response(jsonify(response), status)
