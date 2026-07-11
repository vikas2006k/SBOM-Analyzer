from flask import Blueprint
from app.controllers.dashboard_controller import DashboardController
from app.middlewares.auth_middleware import token_required

dashboard_bp = Blueprint('dashboard', __name__)
dashboard_controller = DashboardController()

@dashboard_bp.route('/summary', methods=['GET'])
@token_required
def get_summary():
    """Retrieve system aggregated metrics."""
    return dashboard_controller.get_summary()

@dashboard_bp.route('/search', methods=['GET'])
@token_required
def global_search():
    """Search applications, libraries, CVEs, and chats."""
    return dashboard_controller.global_search()
