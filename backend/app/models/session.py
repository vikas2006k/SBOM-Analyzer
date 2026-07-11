from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class Session(db.Model, TimestampMixin, SoftDeleteMixin):
    """Session model representing active user sessions."""
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    token = db.Column(db.String(500), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='sessions')

    def __repr__(self):
        return f"<Session user_id={self.user_id} expires_at={self.expires_at}>"
