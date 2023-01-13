from flask import request, Response
from mongoengine.errors import DoesNotExist, ValidationError
from flask_restful import Resource
from datetime import datetime
from database.models import Author
from utils.utils import cursorToJson, objectToJson

class AuthorsApi(Resource):
    def get(self) -> Response:
        cursor = Author.objects()
        authors = cursorToJson(cursor)
        return Response(authors, mimetype="application/json", status=200)

    def post(self) -> Response:
        try:
            body = request.get_json()
            author = Author(**body)
            author.save()
            response, status = author.to_json(), 201
        except Exception as e:
            response, status = objectToJson({"Error": str(e)}), 400

        return Response(response, mimetype="application/json", status=status)

class AuthorApi(Resource):
    def get(self, id: str) -> Response:
        try:
            response, status = Author.objects.get(id=id).to_json(), 200
        except (DoesNotExist, ValidationError):
            response, status = objectToJson({"Error": "Author with given id Does Not Exist!"}), 404

        return Response(response, mimetype="application/json", status=status)

    def put(self, id: str) -> Response:
        try:
            body = request.get_json()
            body['updatedOn'] = datetime.utcnow()
            author = Author.objects.get(id=id).update(**body)
            response, status = {'id': str(id)}, 200
        except DoesNotExist:
            response, status = {"Error": "Author with given id Does Not Exist!"}, 404
        except Exception as e:
            response, status = {"Error": str(e)}, 400

        return Response(objectToJson(response), mimetype="application/json", status=status)

    def delete(self, id: str) -> Response:
        try:
            author = Author.objects.get(id=id)
            author.delete()
            response, status = "", 204
        except (DoesNotExist, ValidationError):
            response, status = objectToJson({"Error": "Author with given id Does Not Exist!"}), 404

        return Response(response, mimetype="application/json", status=status)
