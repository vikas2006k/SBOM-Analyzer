from flask import request
from app.repositories.user_repository import UserRepository
from app.repositories.base_repository import BaseRepository
from app.models.role import Role
from app.utils.crypto_helper import CryptoHelper
from app.utils.jwt_helper import JwtHelper
from app.utils.response_helper import ResponseHelper
from app.utils.logger import Logger

logger = Logger.get_logger('security')

class AuthController:
    """Controller handling account registrations and authentications logic."""

    def __init__(self):
        self.user_repo = UserRepository()
        self.role_repo = BaseRepository(Role)

    def register(self):
        """Register a new user account profile."""
        try:
            data = request.get_json() or {}
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            role_name = data.get("role", "viewer")
            
            if not username or not email or not password:
                return ResponseHelper.error("Missing required registration parameters", 400)
                
            # Verify duplicate account definitions
            if self.user_repo.find_by_username(username):
                return ResponseHelper.error("Username is already registered", 400)
            if self.user_repo.find_by_email(email):
                return ResponseHelper.error("Email address is already registered", 400)

            # Map role
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                # Fallback build default role if database seed was not executed
                role = self.role_repo.create(name=role_name, permissions="[]")

            # Encrypt password
            hashed_pwd = CryptoHelper.hash_password(password)

            # Create User
            user = self.user_repo.create(
                username=username,
                email=email,
                password_hash=hashed_pwd,
                role_id=role.id
            )
            
            logger.info(f"Account registered successfully: {username}")
            return ResponseHelper.success(
                {"id": user.id, "username": user.username, "role": role.name},
                "User account registered successfully",
                201
            )
            
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}", exc_info=True)
            return ResponseHelper.error("Internal Server Error during registration", 500)

    def login(self):
        """Authenticate user credentials and issue JWT token."""
        try:
            data = request.get_json() or {}
            username = data.get("username")
            password = data.get("password")
            
            if not username or not password:
                return ResponseHelper.error("Missing credentials fields", 400)
                
            user = self.user_repo.find_by_username(username)
            if not user or not CryptoHelper.check_password(password, user.password_hash):
                return ResponseHelper.error("Invalid username or password credentials", 401)

            # Issue signed token
            token = JwtHelper.encode_token(user.id)
            
            logger.info(f"User login successful: {username}")
            return ResponseHelper.success({
                "token": token,
                "token_type": "Bearer",
                "expires_in": 24 * 3600,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.name if user.role else "viewer"
                }
            }, "Authentication successful")
            
        except Exception as e:
            logger.error(f"Login failure: {str(e)}", exc_info=True)
            return ResponseHelper.error("Internal Server Error during authentication", 500)
