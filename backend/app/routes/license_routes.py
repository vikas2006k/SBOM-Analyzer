from flask import Blueprint
from app.controllers.license_controller import LicenseController
from app.middlewares.auth_middleware import token_required, roles_allowed

license_bp = Blueprint('licenses', __name__)
license_controller = LicenseController()

@license_bp.route('/application/<int:app_id>', methods=['GET'])
@token_required
def audit_application_licenses(app_id):
    """Audit project dependencies licenses compliance."""
    return license_controller.audit_application_licenses(app_id)

@license_bp.route('/rules', methods=['GET'])
@token_required
def get_license_rules():
    """Retrieve all standard license categories policies."""
    return license_controller.get_license_rules()

@license_bp.route('/rules', methods=['POST'])
@token_required
@roles_allowed('admin', 'security_officer')
def update_license_rule():
    """Update compliance rule parameters."""
    return license_controller.update_license_rule()
