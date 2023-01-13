from flask import request, Response, current_app
from mongoengine.errors import DoesNotExist, ValidationError
from flask_restful import Resource
from datetime import datetime
from database.models import Author
from utils.utils import cursorToJson, objectToJson

class AuthorsApi(Resource):
    def get(self):
        cursor = Author.objects()
        authors = cursorToJson(cursor)
        current_app.logger.info("GET Authors")
        return Response(authors, mimetype="application/json", status=200)

    def post(self):
        try:
            body = request.get_json()
            author = Author(**body)
            author.save()
            response, status = author.to_json(), 201
            current_app.logger.info(f"POST Author {author.id}")
        except Exception as e:
            response, status = objectToJson({"Error": str(e)}), 400
            current_app.logger.error(f"POST Author {str(e)}")

        return Response(response, mimetype="application/json", status=status)

class AuthorApi(Resource):
    def get(self, id):
        try:
            response, status = Author.objects.get(id=id).to_json(), 200
            current_app.logger.info(f"GET Author {id}")
        except (DoesNotExist, ValidationError):
            response, status = objectToJson({"Error": "Author with given id Does Not Exist!"}), 404
            current_app.logger.error(f"GET Author {id} not found")

        return Response(response, mimetype="application/json", status=status)

    def put(self, id):
        try:
            body = request.get_json()
            body['updatedOn'] = datetime.utcnow()
            author = Author.objects.get(id=id).update(**body)
            response, status = {'id': str(id)}, 200
            current_app.logger.info(f"PUT Author {id}")
        except DoesNotExist:
            response, status = {"Error": "Author with given id Does Not Exist!"}, 404
            current_app.logger.error(f"PUT Author {id} not found")
        except Exception as e:
            response, status = {"Error": str(e)}, 400
            current_app.logger.error(f"PUT Author {str(e)}")

        return Response(objectToJson(response), mimetype="application/json", status=status)

    def delete(self, id):
        try:
            author = Author.objects.get(id=id)
            author.delete()
            response, status = "", 204
            current_app.logger.info(f"DELETE Author {author.id}")
        except (DoesNotExist, ValidationError):
            response, status = objectToJson({"Error": "Author with given id Does Not Exist!"}), 404
            current_app.logger.error(f"DELETE Author {id} not found")

        return Response(response, mimetype="application/json", status=status)
