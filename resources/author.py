"""All the Authors API endpoints"""

from datetime import datetime
from flask import request, Response, current_app
from mongoengine.errors import DoesNotExist, ValidationError
from flask_restful import Resource
from flask_expects_json import expects_json
from database.models import Author
from utils.utils import cursor_to_json, object_to_json
from validation.schemas import AUTHOR_SCHEMA, AUTHOR_REQUIRED_FIELDS


class AuthorsApi(Resource):
    """GET and POST API for Authors"""

    def get(self) -> Response:
        """Get all the Authors

        Returns:
            Response: JSON object of all the Authors
        """
        cursor = Author.objects()
        authors = cursor_to_json(cursor)
        current_app.logger.info("GET Authors")
        return Response(authors, mimetype="application/json", status=200)

    @expects_json({**AUTHOR_SCHEMA, "required": AUTHOR_REQUIRED_FIELDS})
    def post(self) -> Response:
        """Create new Author

        Returns:
            Response: JSON object of created Author
        """
        try:
            body = request.get_json()
            author = Author(**body)
            author.save()
            response, status = author.to_json(), 201
            current_app.logger.info(f"POST Author {author.id}")
        except Exception as exp_err:
            response, status = object_to_json({"Error": str(exp_err)}), 400
            current_app.logger.error(f"POST Author {str(exp_err)}")

        return Response(response, mimetype="application/json", status=status)


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
            response, status = (
                object_to_json({"Error": "Author with given id Does Not Exist!"}),
                404,
            )
            current_app.logger.error(f"GET Author {author_id} not found")

        return Response(response, mimetype="application/json", status=status)

    @expects_json(AUTHOR_SCHEMA)
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
            Author.objects.get(id=author_id).update(**body)
            response, status = {"id": str(author_id)}, 200
            current_app.logger.info(f"PUT Author {author_id}")
        except DoesNotExist:
            response, status = {"Error": "Author with given id Does Not Exist!"}, 404
            current_app.logger.error(f"PUT Author {author_id} not found")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"PUT Author {str(exp_err)}")

        return Response(
            object_to_json(response), mimetype="application/json", status=status
        )

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
            response, status = (
                object_to_json({"Error": "Author with given id Does Not Exist!"}),
                404,
            )
            current_app.logger.error(f"DELETE Author {author_id} not found")

        return Response(response, mimetype="application/json", status=status)
