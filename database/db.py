"""Initialize Mongoengine for Database connection"""

from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    """Initialize Database connection with the main app"""
    db.init_app(app)
