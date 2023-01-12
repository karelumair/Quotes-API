from flask import request, Response
from flask_restful import Resource
from datetime import datetime
from database.models import Author
from utils.utils import cursorToJson, objectToJson

class AuthorsApi(Resource):
    def get(self):
        cursor = Author.objects()
        authors = cursorToJson(cursor)
        return Response(authors, mimetype="application/json", status=200)

    def post(self):
        body = request.get_json()
        author = Author(**body).save()
        return Response(author.to_json(), mimetype="application/json", status=200)

class AuthorApi(Resource):
    def get(self, id):
        author = Author.objects.get(id=id)
        return Response(author.to_json(), mimetype="application/json", status=200)

    def put(self, id):
        print("PUT")
        body = request.get_json()
        body['updatedOn'] = datetime.utcnow()
        author = Author.objects.get(id=id).update(**body)
        return {'id': str(id)}, 200

    def delete(self, id):
        Author.objects.get(id=id).delete()
        return '', 200
