from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class Notification(db.Model, TimestampMixin, SoftDeleteMixin):
    """Notification model mapping alert logs directed to analysts."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='notifications')

    def __repr__(self):
        return f"<Notification id={self.id} user={self.user_id} title={self.title} is_read={self.is_read}>"
