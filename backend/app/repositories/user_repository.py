from app.models.user import User
from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):
    """Repository handling custom operations for the User model."""
    def __init__(self):
        super().__init__(User)

    def find_by_username(self, username, include_deleted=False):
        """Find user by username."""
        query = User.query.filter(User.username == username)
        if not include_deleted:
            query = query.filter(User.is_deleted == False)
        return query.first()

    def find_by_email(self, email, include_deleted=False):
        """Find user by email address."""
        query = User.query.filter(User.email == email)
        if not include_deleted:
            query = query.filter(User.is_deleted == False)
        return query.first()

    def search_users(self, search_term, page=1, per_page=10):
        """Search users by username or email with pagination."""
        query = User.query.filter(
            (User.username.ilike(f"%{search_term}%")) | 
            (User.email.ilike(f"%{search_term}%"))
        ).filter(User.is_deleted == False)
        return self.paginate(query, page, per_page)
