from flask import jsonify

class ResponseHelper:
    """Helper structuring REST API JSON response payloads uniformly."""

    @staticmethod
    def success(data=None, message="Operation successful", status_code=200):
        """Format and return a standard successful response payload."""
        response = {
            "success": True,
            "message": message,
            "data": data if data is not None else {}
        }
        return jsonify(response), status_code

    @staticmethod
    def error(message="An error occurred", status_code=400, code="BAD_REQUEST", details=None):
        """Format and return a standard error response payload."""
        response = {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details if details is not None else {}
            }
        }
        return jsonify(response), status_code
