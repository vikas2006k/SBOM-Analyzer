from flask import Blueprint
from app.controllers.app_controller import AppController
from app.middlewares.auth_middleware import token_required

app_bp = Blueprint('applications', __name__)
app_controller = AppController()

@app_bp.route('/<int:app_id>', methods=['GET'])
@token_required
def get_application(app_id):
    """Endpoint: Get application details metadata.
    Authentication: Required
    """
    return app_controller.get_application(app_id)

@app_bp.route('/<int:app_id>/graph', methods=['GET'])
@token_required
def get_application_graph(app_id):
    """Endpoint: Get visual graph nodes/edges for React Flow.
    Authentication: Required
    """
    return app_controller.get_application_graph(app_id)

@app_bp.route('/<int:app_id>/dependencies', methods=['GET'])
@token_required
def get_application_dependencies(app_id):
    """Endpoint: Get flat list of dependencies with depth levels.
    Authentication: Required
    """
    return app_controller.get_application_dependencies(app_id)
