import jwt
from datetime import datetime, timedelta
from flask import current_app

class JwtHelper:
    """Utility handling JWT signing and validation workflows."""

    @staticmethod
    def encode_token(user_id, expires_hours=24):
        """Generate a signed JWT token for a specific user ID."""
        try:
            secret = current_app.config.get("JWT_SECRET_KEY", "fallback-secret")
            payload = {
                "exp": datetime.utcnow() + timedelta(hours=expires_hours),
                "iat": datetime.utcnow(),
                "sub": user_id
            }
            token = jwt.encode(payload, secret, algorithm="HS256")
            # PyJWT returns a string in newer versions, or bytes in older.
            if isinstance(token, bytes):
                return token.decode('utf-8')
            return token
        except Exception as e:
            raise RuntimeError(f"JWT Token signing failed: {str(e)}")

    @staticmethod
    def decode_token(token):
        """Decode and validate a JWT access token signature."""
        try:
            secret = current_app.config.get("JWT_SECRET_KEY", "fallback-secret")
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token signature has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid verification token signature")
