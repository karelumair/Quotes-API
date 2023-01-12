from .db import db
import datetime
from utils.utils import objectToJson

class Author(db.Document):
    name = db.StringField(required=True)
    DOB = db.DateTimeField(required=True)
    country = db.StringField(required=True)
    description = db.StringField(required=True)
    createdOn = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedOn = db.DateTimeField(default=datetime.datetime.utcnow)
    meta = {'collection': 'authors'}

    def to_json(self):
        obj = self.to_mongo()
        return objectToJson(obj)


class Quote(db.Document):
    quote = db.StringField(required=True)
    author = db.ReferenceField(Author, reverse_delete_rule=db.CASCADE, dbref=False)
    tags = db.ListField(db.StringField(), required=True)
    createdOn = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedOn = db.DateTimeField(default=datetime.datetime.utcnow)
    meta = {'collection': 'quotes'}

    def to_json(self):
        obj = self.to_mongo()
        obj["author"] = {"name": self.author.name, "id": self.author.id}
        return objectToJson(obj)
