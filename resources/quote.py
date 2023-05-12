"""All the Quotes API endpoints"""

from datetime import datetime, timezone
from flask import Response, request, jsonify, make_response, current_app
from mongoengine.errors import DoesNotExist, ValidationError, NotUniqueError
from flask_restful import Resource
from flask_pydantic import validate
from flask_jwt_extended import get_jwt_identity, jwt_required
from database.models import Quote, Author
from database.schemas import QuoteSchema, QuoteUpdateSchema
from utils.utils import cursor_to_json, quote_aggregate_to_json
from constants.app_constants import QUOTE_PER_PAGE


class QuotesApi(Resource):
    """GET and POST API for Quotes"""

    @jwt_required()
    def get(self) -> Response:
        """Get all the Quotes

        Returns:
            Response: JSON object of all the Quotes
        """
        current_app.logger.info("GET Authors - REQUEST RECEIVED")

        tags = request.args.get("tags", None)
        page = int(request.args.get("page", 1))
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
                {
                    "$lookup": {
                        "from": "authors",
                        "localField": "author",
                        "foreignField": "_id",
                        "as": "author",
                    }
                },
                {"$set": {"author": {"$arrayElemAt": ["$author", 0]}}},
                {
                    "$project": {
                        "matchedCount": 0,
                        "scrapedAuthor": 0,
                        "author.dob": 0,
                        "author.country": 0,
                        "author.description": 0,
                        "author.createdOn": 0,
                        "author.updatedOn": 0,
                        "author.scrapeId": 0,
                    }
                },
            ]
            cursor = (
                Quote.objects(author__exists=True)
                .order_by("-createdOn")
                .aggregate(pipeline)
            )
            quotes = quote_aggregate_to_json(cursor)
            current_app.logger.info(
                f"GET Quotes by tags {tags} - FETCHED {len(quotes)} Quotes"
            )
        else:
            cursor = (
                Quote.objects(author__exists=True)
                .order_by("-createdOn")
                .exclude("scrapedAuthor")
                .paginate(page=page, per_page=QUOTE_PER_PAGE)
                .items
            )
            quotes = cursor_to_json(cursor)
            current_app.logger.info(f"GET Quotes - FETCHED {len(quotes)} Quotes")

        return make_response(jsonify(quotes), 200)

    @jwt_required()
    @validate()
    def post(self, body: QuoteSchema) -> Response:
        """Create new Quote

        Returns:
            Response: JSON object of created Quote
        """
        current_app.logger.info("POST Quote - REQUEST RECEIVED")

        try:
            author_id = get_jwt_identity()
            # Check if author exists else throw DoesNotExist exception
            Author.objects.get(id=author_id)

            quote = Quote(**body.dict(), author=author_id, createdBy="author")
            quote.save()

            response, status = quote.to_json(), 201
            current_app.logger.info(f"POST Quote - ADDED Quote Id:{quote.id}")
        except NotUniqueError:
            response, status = {"Error": "Quote Already Exist"}, 400
            current_app.logger.error("POST Quote - DUPLICATE QUOTE")
        except DoesNotExist:
            response, status = {"Error": "Author id Does Not Exist!"}, 404
            current_app.logger.error(f"POST Quote - Author Id:{body.author} NOT FOUND")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"POST Quote - {str(exp_err)}")

        return make_response(jsonify(response), status)


class QuoteApi(Resource):
    """GET Detail, PUT, and DELETE API for Quotes"""

    @jwt_required()
    @validate()
    def put(self, quote_id: str, body: QuoteUpdateSchema) -> Response:
        """Update single Quote with given id

        Args:
            id (str): Quote id

        Returns:
            Response: JSON object of Quote
        """
        current_app.logger.info(f"PUT Quote Id:{quote_id} - RECEIVED REQUEST")

        try:
            author_id = get_jwt_identity()
            quote = Quote.objects.get(id=quote_id)

            if author_id != str(quote.author.id):
                return make_response(jsonify({"Error": "Not Authorized"}), 401)

            quote.update(
                **body.dict(exclude_unset=True),
                updatedOn=datetime.now(timezone.utc),
                updatedBy="author",
            )

            response, status = {"id": quote_id}, 200
            current_app.logger.info(f"PUT Quote Id:{quote_id} - UPDATED")
        except NotUniqueError:
            response, status = {"Error": "Quote Already Exist"}, 400
            current_app.logger.error("POST Quote - DUPLICATE QUOTE")
        except DoesNotExist:
            response, status = {"Error": "Quote with given id Does Not Exist!"}, 404
            current_app.logger.error(f"PUT Quote Id:{quote_id} - NOT FOUND")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"PUT Quote Id:{quote_id} - {str(exp_err)}")

        return make_response(jsonify(response), status)

    @jwt_required()
    def delete(self, quote_id: str) -> Response:
        """Delete single Quote with given id

        Args:
            id (str): Quote id

        Returns:
            Response: Empty
        """
        current_app.logger.info(f"DELETE Quote Id:{quote_id} - RECEIVED REQUEST")

        try:
            author_id = get_jwt_identity()
            quote = Quote.objects.get(id=quote_id)

            if author_id != str(quote.author.id):
                return make_response(jsonify({"Error": "Not Authorized"}), 401)

            quote.delete()
            response, status = "", 204
            current_app.logger.info(f"DELETE Quote Id:{quote_id} - DELETED")
        except (DoesNotExist, ValidationError):
            response, status = {"Error": "Quote with given id Does Not Exist!"}, 404
            current_app.logger.error(f"DELETE Quote Id:{quote_id} - NOT FOUND")

        return make_response(jsonify(response), status)

    @jwt_required()
    def get(self, quote_id: str) -> Response:
        """Get single Quote with given id

        Args:
            id (str): Quote id

        Returns:
            Response: JSON object of Quote
        """
        current_app.logger.info(f"GET Quote Id:{quote_id} - RECEIVED REQUEST")

        try:
            quote = Quote.objects.exclude("scrapedAuthor").get(id=quote_id)
            response, status = quote.to_json(), 200
            current_app.logger.info(f"GET Quote Id:{quote_id} - FETCHED")
        except (DoesNotExist, ValidationError):
            response, status = {"Error": "Quote with given id Does Not Exist!"}, 404
            current_app.logger.error(f"GET Quote Id:{quote_id} - NOT FOUND")

        return make_response(jsonify(response), status)


class QuotePaginateApi(Resource):
    """GET API for Quotes Pagination Info"""

    @jwt_required()
    def get(self, page: str):
        """Get prev and next for a page

        Args:
            page (str): page number

        Returns:
            Response: JSON response
        """
        page = int(page)
        try:
            paginate = Quote.objects(author__exists=True).paginate(
                page=page, per_page=QUOTE_PER_PAGE
            )
            response, status = {
                "has_next": paginate.has_next,
                "has_prev": paginate.has_prev,
            }, 200
            current_app.logger.info(f"GET Page:{page} - FETCHED")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 404
            current_app.logger.error(f"GET Page:{page} - {str(exp_err)}")

        return make_response(jsonify(response), status)
