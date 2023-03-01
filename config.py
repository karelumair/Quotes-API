"""Contains all the configuration of the Flask App"""

from os import environ
from pydantic import BaseSettings


class GlobalConfig(BaseSettings):
    """Global Configurations"""

    MONGODB_SETTINGS: list = [
        {
            "HOST": environ.get("MONGODB_HOST", "localhost"),
            "PORT": environ.get("MONGODB_PORT", 27017),
            "DB": environ.get("MONGODB_DATABASE"),
            "USERNAME": environ.get("MONGODB_USERNAME"),
            "PASSWORD": environ.get("MONGODB_PASSWORD"),
        }
    ]
    CELERY: dict = {
        "BROKER_URL": environ.get("CELERY_BROKER_URL"),
        "RESULT_BACKEND": environ.get("CELERY_RESULT_BACKEND"),
    }


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
