from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class AIConversation(db.Model, TimestampMixin, SoftDeleteMixin):
    """AIConversation model holding chat logs and state variables."""
    __tablename__ = 'ai_conversations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, index=True)
    message_history = db.Column(db.Text, nullable=False, default="[]")  # JSON String of message objects

    # Relationships
    user = db.relationship('User', back_populates='conversations')
    application = db.relationship('Application', back_populates='conversations')

    def __repr__(self):
        return f"<AIConversation id={self.id} user={self.user_id} app={self.application_id}>"
