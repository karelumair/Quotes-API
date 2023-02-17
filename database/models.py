"""All the Data Models"""

import datetime
from database.db import db


class Author(db.Document):
    """Author Model"""

    name = db.StringField(required=True)
    dob = db.DateTimeField(required=True)
    country = db.StringField(required=True)
    description = db.StringField(required=True)
    scrapeId = db.ObjectIdField()
    createdOn = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedOn = db.DateTimeField(default=datetime.datetime.utcnow)
    meta = {"collection": "authors"}

    def to_json(self, *args, **kwargs):
        obj = self.to_mongo().to_dict()
        obj["_id"] = str(obj["_id"])
        return obj


class ScrapedAuthor(db.Document):
    """Scraped Author Model"""

    name = db.StringField()
    dob = db.DateTimeField()
    country = db.StringField()
    description = db.StringField()
    link = db.StringField()
    createdOn = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedOn = db.DateTimeField(default=datetime.datetime.utcnow)
    meta = {"collection": "scrapedAuthors"}

    def to_json(self, *args, **kwargs):
        obj = self.to_mongo().to_dict()
        obj["_id"] = str(obj["_id"])
        return obj


class Quote(db.Document):
    """Quote Model"""

    quote = db.StringField(required=True)
    author = db.ReferenceField(Author, reverse_delete_rule=db.CASCADE, dbref=False)
    scrapedAuthor = db.ReferenceField(
        ScrapedAuthor, reverse_delete_rule=db.CASCADE, dbref=False
    )
    tags = db.ListField(db.StringField())
    createdOn = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedOn = db.DateTimeField(default=datetime.datetime.utcnow)
    meta = {"collection": "quotes"}

    def to_json(self, *args, **kwargs):
        obj = self.to_mongo().to_dict()
        obj["_id"] = str(obj["_id"])
        obj["author"] = {"name": self.author.name, "id": str(self.author.id)}
        return obj
