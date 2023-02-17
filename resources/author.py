"""All the Authors API endpoints"""

from datetime import datetime
from flask import request, Response, jsonify, make_response, current_app
from mongoengine.errors import DoesNotExist, ValidationError
from flask_restful import Resource
from database.models import Author
from database.schemas import AuthorSchema, AuthorUpdateSchema
from utils.utils import cursor_to_json


class AuthorsApi(Resource):
    """GET and POST API for Authors"""

    def get(self) -> Response:
        """Get all the Authors

        Returns:
            Response: JSON object of all the Authors
        """
        cursor = Author.objects().exclude("scrapeId")
        authors = cursor_to_json(cursor)
        current_app.logger.info("GET Authors")
        return make_response(jsonify(authors), 200)

    def post(self) -> Response:
        """Create new Author

        Returns:
            Response: JSON object of created Author
        """
        try:
            body = request.get_json()
            author_validate = AuthorSchema(**body)
            author = Author(**author_validate.dict())
            author.save()
            response, status = author.to_json(), 201
            current_app.logger.info(f"POST Author {author.id}")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"POST Author {str(exp_err)}")

        return make_response(jsonify(response), status)


class AuthorApi(Resource):
    """GET Detail, PUT, and DELETE API for Authors"""

    def get(self, author_id: str) -> Response:
        """Get single Author with given id

        Args:
            id (str): Author id

        Returns:
            Response: JSON object of Author
        """
        try:
            response, status = Author.objects.get(id=author_id).to_json(), 200
            current_app.logger.info(f"GET Author {author_id}")
        except (DoesNotExist, ValidationError):
            response, status = {"Error": "Author with given id Does Not Exist!"}, 404
            current_app.logger.error(f"GET Author {author_id} not found")

        return make_response(jsonify(response), status)

    def put(self, author_id: str) -> Response:
        """Update single Author with given id

        Args:
            id (str): Author id

        Returns:
            Response: JSON object of created Author
        """
        try:
            body = request.get_json()
            body["updatedOn"] = datetime.utcnow()

            author_validate = AuthorUpdateSchema(**body)
            update_values = {
                k: v for k, v in author_validate.dict().items() if v is not None
            }
            Author.objects.get(id=author_id).update(**update_values)

            response, status = {"id": str(author_id)}, 200
            current_app.logger.info(f"PUT Author {author_id}")
        except DoesNotExist:
            response, status = {"Error": "Author with given id Does Not Exist!"}, 404
            current_app.logger.error(f"PUT Author {author_id} not found")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"PUT Author {str(exp_err)}")

        return make_response(jsonify(response), status)

    def delete(self, author_id: str) -> Response:
        """Delete single Author with given id

        Args:
            id (str): Author id

        Returns:
            Response: Empty
        """
        try:
            author = Author.objects.get(id=author_id)
            author.delete()
            response, status = "", 204
            current_app.logger.info(f"DELETE Author {author.id}")
        except (DoesNotExist, ValidationError):
            response, status = {"Error": "Author with given id Does Not Exist!"}, 404
            current_app.logger.error(f"DELETE Author {author_id} not found")

        return make_response(jsonify(response), status)
