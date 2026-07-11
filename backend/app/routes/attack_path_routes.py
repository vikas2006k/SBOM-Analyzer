from flask import Blueprint
from app.controllers.attack_path_controller import AttackPathController
from app.middlewares.auth_middleware import token_required

attack_path_bp = Blueprint('attack_paths', __name__)
attack_path_controller = AttackPathController()

@attack_path_bp.route('/application/<int:app_id>', methods=['GET'])
@token_required
def get_attack_paths(app_id):
    """Retrieve reachability attack path reports."""
    return attack_path_controller.get_attack_paths(app_id)
