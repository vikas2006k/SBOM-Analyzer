import re

class ValidationHelper:
    """Utility containing validation logic for common formats (email, passwords)."""

    @staticmethod
    def is_valid_email(email):
        """Validate email format utilizing regex rules."""
        if not email:
            return False
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(email_regex, email))

    @staticmethod
    def is_strong_password(password):
        """Verify password complexity constraints (min 8 characters, digit, letter)."""
        if not password or len(password) < 8:
            return False
        has_digit = any(char.isdigit() for char in password)
        has_letter = any(char.isalpha() for char in password)
        return has_digit and has_letter
