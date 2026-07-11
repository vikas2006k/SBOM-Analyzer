from functools import wraps
from flask import request, g
from app.middlewares.error_middleware import AuthenticationError, ForbiddenError, AppException
from app.utils.jwt_helper import JwtHelper
from app.models.user import User

def token_required(f):
    """Decorator checking JWT tokens signatures on HTTP headers."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token = None
        
        if auth_header:
            try:
                parts = auth_header.split()
                if parts[0].lower() == "bearer" and len(parts) == 2:
                    token = parts[1]
                else:
                    raise AuthenticationError("Authorization header format must be Bearer <token>")
            except Exception:
                raise AuthenticationError("Authorization header format must be Bearer <token>")
        else:
            token = request.args.get("token")

        if not token:
            raise AuthenticationError("Authorization header or token parameter is missing")

        try:
            payload = JwtHelper.decode_token(token)
            
            # Retrieve active user from database
            user_id = payload.get("sub")
            user = User.query.filter(User.id == user_id, User.is_deleted == False).first()
            if not user:
                raise AuthenticationError("Associated account is inactive or not found")
            
            # Save user identity in Flask context
            g.current_user = user
            g.current_role = user.role.name if user.role else "viewer"
            
        except Exception as e:
            if isinstance(e, AppException):
                raise e
            raise AuthenticationError(f"Token parsing failed: {str(e)}")

        return f(*args, **kwargs)
    return decorated

def roles_allowed(*roles):
    """Decorator validating user authorization roles permissions."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Enforce token verification first if not already done
            if not hasattr(g, 'current_role'):
                raise AuthenticationError("Identity verification context is missing")
            
            if g.current_role not in roles:
                raise ForbiddenError(f"Access restricted. Required roles: {list(roles)}")
                
            return f(*args, **kwargs)
        return decorated
    return decorator
