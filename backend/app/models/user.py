from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class User(db.Model, TimestampMixin, SoftDeleteMixin):
    """User model representing application users."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    # Relationships
    role = db.relationship('Role', back_populates='users')
    sessions = db.relationship('Session', back_populates='user', cascade="all, delete-orphan")
    uploads = db.relationship('SBOMUpload', back_populates='uploader', lazy=True)
    reports = db.relationship('AnalysisReport', back_populates='generator', lazy=True)
    conversations = db.relationship('AIConversation', back_populates='user', lazy=True)
    audit_logs = db.relationship('AuditLog', back_populates='user', lazy=True)
    notifications = db.relationship('Notification', back_populates='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"
