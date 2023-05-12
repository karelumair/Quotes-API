"""All the Data Models"""

import datetime
from database.db import db
from constants.app_constants import SCRAPED_DATA_CLEAN_UP_DURATION
from services.scraper.utils import ScrapingTask


class Author(db.Document):
    """Author Model"""

    name = db.StringField(required=True, unique=True)
    password = db.StringField(default="")
    dob = db.DateField(required=True)
    country = db.StringField(required=True)
    description = db.StringField(required=True)
    scrapeId = db.ObjectIdField()
    createdBy = db.StringField()
    updatedBy = db.StringField()
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
    meta = {
        "collection": "scrapedAuthors",
        "indexes": [
            {
                "fields": ["updatedOn"],
                "expireAfterSeconds": SCRAPED_DATA_CLEAN_UP_DURATION,
            }
        ],
    }

    def to_json(self, *args, **kwargs):
        obj = self.to_mongo().to_dict()
        obj["_id"] = str(obj["_id"])
        return obj


class Quote(db.Document):
    """Quote Model"""

    quote = db.StringField(required=True, unique=True)
    author = db.ReferenceField(Author, reverse_delete_rule=db.CASCADE, dbref=False)
    scrapedAuthor = db.ReferenceField(
        ScrapedAuthor, reverse_delete_rule=db.CASCADE, dbref=False
    )
    tags = db.ListField(db.StringField())
    createdBy = db.StringField()
    updatedBy = db.StringField()
    createdOn = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedOn = db.DateTimeField(default=datetime.datetime.utcnow)
    meta = {"collection": "quotes"}

    def to_json(self, *args, **kwargs):
        obj = self.to_mongo().to_dict()
        obj["_id"] = str(obj["_id"])
        obj["author"] = {"name": self.author.name, "id": str(self.author.id)}
        return obj


class ScheduledTask(db.Document):
    """Scheduled Tasks Model"""

    jobId = db.StringField()
    celeryTask = db.StringField()
    description = db.StringField()
    status = db.DictField(default=ScrapingTask().to_dict())
    createdOn = db.DateTimeField(default=datetime.datetime.utcnow)
    meta = {"collection": "scheduledTasks"}

    def to_json(self, *args, **kwargs):
        obj = self.to_mongo().to_dict()
        obj["_id"] = str(obj["_id"])
        return obj


class LoginToken(db.Document):
    """Login Token Model"""

    author_id = db.ObjectIdField()
    access = db.StringField(required=True)
    refresh = db.StringField(required=True)
    createdOn = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedOn = db.DateTimeField(default=datetime.datetime.utcnow)
    meta = {"collection": "login_tokens"}

    def to_json(self, *args, **kwargs):
        obj = self.to_mongo().to_dict()
        obj["_id"] = str(obj["_id"])
        return obj
