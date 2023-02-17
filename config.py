"""Contains all the configuration of the Flask App"""

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

MONGO_URI = os.environ.get("MONGO_URI")
MONGO_TEST_URI = os.environ.get("MONGO_TEST_URI")
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")


CONFIG = {
    "test": {
        "MONGODB_SETTINGS": {"host": MONGO_TEST_URI},
        "CELERY": {
            "broker_url": CELERY_BROKER_URL,
            "result_backend": CELERY_BROKER_URL,
        },
        # This mode ensures exceptions are propagated rather than handled by the app's error handlers.
        "TESTING": True,
    },
    "prod": {
        "MONGODB_SETTINGS": {"host": MONGO_URI},
        "CELERY": {
            "broker_url": CELERY_BROKER_URL,
            "result_backend": CELERY_BROKER_URL,
        },
    },
}
