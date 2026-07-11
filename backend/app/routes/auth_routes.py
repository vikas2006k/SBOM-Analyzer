from flask import Blueprint
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)
auth_controller = AuthController()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint: Register a new analyst account.
    Authentication: None
    """
    return auth_controller.register()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint: Authenticate user credentials and retrieve token.
    Authentication: None
    """
    return auth_controller.login()
