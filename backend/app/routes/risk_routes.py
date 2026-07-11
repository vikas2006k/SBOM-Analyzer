from flask import Blueprint
from app.controllers.risk_controller import RiskController
from app.middlewares.auth_middleware import token_required, roles_allowed

risk_bp = Blueprint('risk', __name__)
risk_controller = RiskController()

@risk_bp.route('/application/<int:app_id>', methods=['GET'])
@token_required
def get_application_risk(app_id):
    """Retrieve composite risk reports metrics."""
    return risk_controller.get_application_risk(app_id)

@risk_bp.route('/application/<int:app_id>/calculate', methods=['POST'])
@token_required
@roles_allowed('admin', 'security_officer')
def calculate_application_risk(app_id):
    """Recalculate composite risk reports parameters."""
    return risk_controller.calculate_application_risk(app_id)
