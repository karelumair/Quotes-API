"""Contains all the configuration of the Flask App"""

from os import environ
from pydantic import BaseSettings


class GlobalConfig(BaseSettings):
    """Global Configurations"""

    MONGODB_SETTINGS: list = [
        {
            "HOST": environ.get("MONGODB_HOST", "localhost"),
            "PORT": int(environ.get("MONGODB_PORT", 27017)),
            "DB": environ.get("MONGODB_DATABASE"),
            "USERNAME": environ.get("MONGODB_USERNAME"),
            "PASSWORD": environ.get("MONGODB_PASSWORD"),
        }
    ]
    CELERY: dict = {
        "broker_url": environ.get("CELERY_BROKER_URL"),
        "result_backend": environ.get("CELERY_RESULT_BACKEND"),
    }
    LIMITER_STORAGE_URI: str = environ.get("LIMITER_STORAGE_URI")


class DevConfig(GlobalConfig):
    """Development Configurations"""

    DEBUG: bool = True


class TestConfig(GlobalConfig):
    """Test Configurations"""

    TESTING: bool = True


configs = {
    "dev": DevConfig().dict(),
    "test": TestConfig().dict(),
    "prod": GlobalConfig().dict(),
}

CONFIG = configs[environ.get("ENV", "prod")]
