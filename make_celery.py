"""Creates celery App for starting celery workers"""

from app import create_app

flask_app = create_app(context="celery")
celery = flask_app.extensions["celery"]
