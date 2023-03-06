"""Initialize Rate Limiter for endpoints"""

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import CONFIG

limiter = Limiter(
    key_func=get_remote_address, storage_uri=CONFIG["LIMITER_STORAGE_URI"]
)


def init_limiter(app: Flask):
    """Initialize Rate Limiter"""

    limiter.init_app(app)
