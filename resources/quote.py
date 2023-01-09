from flask import Response, request
from database.models import Quote
from flask_restful import Resource

class QuotesApi(Resource):
    def get(self):
        quotes = Quote.objects().to_json()
        return Response(quotes, mimetype="application/json", status=200)

    def post(self):
        body = request.get_json()
        movie =  Quote(**body).save()
        id = movie.id
        return {'id': str(id)}, 200
        
class QuoteApi(Resource):
    def put(self, id):
        body = request.get_json()
        Quote.objects.get(id=id).update(**body)
        return {'id': str(id)}, 200
    
    def delete(self, id):
        movie = Quote.objects.get(id=id).delete()
        return '', 200

    def get(self, id):
        quotes = Quote.objects.get(id=id).to_json()
        return Response(quotes, mimetype="application/json", status=200)