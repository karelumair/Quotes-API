"""Handling Errors to give valid JSON response"""

from flask import Blueprint
from jsonschema import ValidationError

error_handler_blueprint = Blueprint("error_handlers", __name__)


@error_handler_blueprint.errorhandler(ValidationError)
def bad_request(error):
    """Returns JSON response for data validation errors"""

    original_error = error.description
    return {
        "Field": original_error.relative_schema_path[1],
        "Error": original_error.message,
    }, 400
