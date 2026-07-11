from flask import Blueprint
from app.controllers.maintenance_controller import MaintenanceController
from app.middlewares.auth_middleware import token_required

maintenance_bp = Blueprint('maintenance', __name__)
maintenance_controller = MaintenanceController()

@maintenance_bp.route('/application/<int:app_id>', methods=['GET'])
@token_required
def get_application_maintenance(app_id):
    """Retrieve maintenance score breakdown details for an application."""
    return maintenance_controller.get_application_maintenance(app_id)
