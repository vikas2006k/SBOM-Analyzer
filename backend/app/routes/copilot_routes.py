from flask import Blueprint
from app.controllers.copilot_controller import CopilotController
from app.middlewares.auth_middleware import token_required

copilot_bp = Blueprint('copilot', __name__)
copilot_controller = CopilotController()

@copilot_bp.route('/chat', methods=['POST'])
@token_required
def chat():
    """Send natural language question to Copilot."""
    return copilot_controller.chat()

@copilot_bp.route('/history/<int:app_id>', methods=['GET'])
@token_required
def get_history(app_id):
    """Retrieve chat history logs."""
    return copilot_controller.get_history(app_id)
