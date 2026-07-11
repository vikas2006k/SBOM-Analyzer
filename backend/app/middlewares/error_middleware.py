from flask import jsonify
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError as PydanticValidationError

class AppException(Exception):
    """Base application exception for custom error classifications."""
    def __init__(self, message, status_code=400, code="BAD_REQUEST", details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}

class AuthenticationError(AppException):
    """Exception representing token signature or login errors."""
    def __init__(self, message="Authentication credentials failed", details=None):
        super().__init__(message, status_code=401, code="UNAUTHORIZED", details=details)

class ForbiddenError(AppException):
    """Exception representing authorization level violations."""
    def __init__(self, message="Access forbidden to requested resource", details=None):
        super().__init__(message, status_code=403, code="FORBIDDEN", details=details)

class NotFoundError(AppException):
    """Exception representing missing database references."""
    def __init__(self, message="Resource not found", details=None):
        super().__init__(message, status_code=404, code="NOT_FOUND", details=details)

class DatabaseError(AppException):
    """Exception representing SQL exceptions."""
    def __init__(self, message="Database transaction failed", details=None):
        super().__init__(message, status_code=500, code="DATABASE_ERROR", details=details)

class BusinessException(AppException):
    """Exception representing logical exceptions in services."""
    def __init__(self, message, details=None):
        super().__init__(message, status_code=422, code="UNPROCESSABLE_ENTITY", details=details)

def register_error_handlers(app):
    """Register custom global exception handlers to Flask app context."""
    
    @app.errorhandler(AppException)
    def handle_app_exception(error):
        response = {
            "success": False,
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details
            }
        }
        return jsonify(response), error.status_code

    @app.errorhandler(PydanticValidationError)
    def handle_pydantic_validation_error(error):
        response = {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation parameters failed",
                "details": error.errors()
            }
        }
        return jsonify(response), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = {
            "success": False,
            "error": {
                "code": error.name.upper().replace(" ", "_"),
                "message": error.description,
                "details": {}
            }
        }
        return jsonify(response), error.code

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        # In development, you can inspect stack traces
        app.logger.error(f"Generic error caught: {str(error)}", exc_info=True)
        response = {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected system error occurred.",
                "details": {"error_str": str(error)} if app.debug else {}
            }
        }
        return jsonify(response), 500
