from flask import Blueprint
from app.controllers.report_controller import ReportController
from app.middlewares.auth_middleware import token_required

report_bp = Blueprint('reports', __name__)
report_controller = ReportController()

@report_bp.route('/pdf/<int:app_id>', methods=['GET'])
@token_required
def download_pdf(app_id):
    """Download executive security PDF."""
    return report_controller.download_pdf(app_id)

@report_bp.route('/csv/<int:app_id>', methods=['GET'])
@token_required
def download_csv(app_id):
    """Download developer patching manifest CSV."""
    return report_controller.download_csv(app_id)
