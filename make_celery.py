"""Creates celery App for starting celery workers"""

from app import create_app

flask_app = create_app("prod")
celery = flask_app.extensions["celery"]
