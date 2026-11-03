from flask import jsonify
from marshmallow import ValidationError

class APIException(Exception):
    def __init__(self, message: str, status_code: int = 400, error_name: str = "Bad Request"):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.error_name = error_name

class NotFound(APIException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404, error_name="Not Found")

class Conflict(APIException):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message=message, status_code=409, error_name="Conflict")

def register_error_handlers(app):
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        return jsonify({
            "status code": error.status_code,
            "error": error.error_name,
            "detail": error.message
        }), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({
            "status code": 422,
            "error": "Unprocessable Entity",
            "detail": error.messages
        }), 422

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({
            "status code": 404,
            "error": "Not Found",
            "detail": "Endpoint not found"
        }), 404