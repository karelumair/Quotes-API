from .db import db
import datetime

class Quote(db.Document):
    quote = db.StringField(required=True)
    quoteBy = db.StringField(required=True)
    tags = db.ListField(db.StringField(), required=True)
    createdOn = db.DateTimeField(default=datetime.datetime.utcnow)
    updatedOn = db.DateTimeField(default=datetime.datetime.utcnow)
    meta = {'collection': 'quotes'}