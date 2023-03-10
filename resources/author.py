"""All the Authors API endpoints"""

from datetime import datetime, timezone
from flask import Response, jsonify, make_response, current_app
from mongoengine.errors import DoesNotExist, ValidationError, NotUniqueError
from flask_restful import Resource
from flask_pydantic import validate
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
        current_app.logger.info("GET Authors - REQUEST RECEIVED")

        cursor = Author.objects().exclude("scrapeId")
        authors = cursor_to_json(cursor)

        current_app.logger.info(f"GET Authors - FETCHED {len(authors)} Authors")
        return make_response(jsonify(authors), 200)

    @validate()
    def post(self, body: AuthorSchema) -> Response:
        """Create new Author

        Returns:
            Response: JSON object of created Author
        """
        current_app.logger.info("POST Author - REQUEST RECEIVED")

        try:
            author = Author(**body.dict(), createdBy="author")
            author.save()

            response, status = author.to_json(), 201
            current_app.logger.info(f"POST Author - ADDED Author Id:{author.id}")
        except NotUniqueError:
            response, status = {"Error": "Author Name Already Exist"}, 400
            current_app.logger.error("POST Author - DUPLICATE AUTHOR NAME")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"POST Author - {str(exp_err)}")

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
        current_app.logger.info(f"GET Author Id:{author_id} - RECEIVED REQUEST")

        try:
            author = Author.objects.exclude("scrapeId").get(id=author_id)
            response, status = author.to_json(), 200
            current_app.logger.info(f"GET Author Id:{author_id} - FETCHED")
        except (DoesNotExist, ValidationError):
            response, status = {"Error": "Author with given id Does Not Exist!"}, 404
            current_app.logger.error(f"GET Author Id:{author_id} - NOT FOUND")

        return make_response(jsonify(response), status)

    @validate()
    def put(self, author_id: str, body: AuthorUpdateSchema) -> Response:
        """Update single Author with given id

        Args:
            id (str): Author id

        Returns:
            Response: JSON object of created Author
        """
        current_app.logger.info(f"PUT Author Id:{author_id} - RECEIVED REQUEST")

        try:
            Author.objects.get(id=author_id).update(
                **body.dict(exclude_unset=True),
                updatedOn=datetime.now(timezone.utc),
                updatedBy="author",
            )

            response, status = {"id": author_id}, 200
            current_app.logger.info(f"PUT Author Id:{author_id} - UPDATED")
        except NotUniqueError:
            response, status = {"Error": "Author Name Already Exist"}, 400
            current_app.logger.error("POST Author - DUPLICATE AUTHOR NAME")
        except DoesNotExist:
            response, status = {"Error": "Author with given id Does Not Exist!"}, 404
            current_app.logger.error(f"PUT Author Id:{author_id} - NOT FOUND")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"PUT Author Id:{author_id} - {str(exp_err)}")

        return make_response(jsonify(response), status)

    def delete(self, author_id: str) -> Response:
        """Delete single Author with given id

        Args:
            id (str): Author id

        Returns:
            Response: Empty
        """
        current_app.logger.info(f"DELETE Author Id:{author_id} - RECEIVED REQUEST")

        try:
            author = Author.objects.get(id=author_id)
            author.delete()
            response, status = "", 204
            current_app.logger.info(f"DELETE Author Id:{author_id} - DELETED")
        except (DoesNotExist, ValidationError):
            response, status = {"Error": "Author with given id Does Not Exist!"}, 404
            current_app.logger.error(f"DELETE Author Id:{author_id} - NOT FOUND")

        return make_response(jsonify(response), status)
