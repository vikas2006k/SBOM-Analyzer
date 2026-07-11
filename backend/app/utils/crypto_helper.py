import bcrypt

class CryptoHelper:
    """Utility handling password encryption and validations using bcrypt."""

    @staticmethod
    def hash_password(password):
        """Encrypt password using bcrypt hashing algorithm."""
        if not password:
            raise ValueError("Password cannot be empty")
        # Ensure password is bytes
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def check_password(password, hashed_password):
        """Validate cleartext password match against database hash."""
        if not password or not hashed_password:
            return False
        try:
            pwd_bytes = password.encode('utf-8')
            hash_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(pwd_bytes, hash_bytes)
        except Exception:
            return False
