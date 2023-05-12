"""Initialize JWT Manager"""

from flask_jwt_extended import JWTManager
from mongoengine.errors import DoesNotExist
from database.models import LoginToken

jwt = JWTManager()


def init_jwt(app):
    """Initialize the JWT Manager with app

    Args:
        app (Flask): Flask app to initialize JWT Manager with
    """

    jwt.init_app(app)

    # Token Blocklist function
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload: dict) -> bool:
        """Check if token is blocked or not"""
        # pylint: disable=unused-argument

        jti = jwt_payload["jti"]

        try:
            if jwt_payload["type"] == "access":
                token = LoginToken.objects.get(access=jti)
            else:
                token = LoginToken.objects.get(refresh=jti)
        except DoesNotExist:
            token = None

        return token is None
