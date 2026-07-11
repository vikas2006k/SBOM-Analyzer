from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class AuditLog(db.Model, TimestampMixin, SoftDeleteMixin):
    """AuditLog model tracking administrative and security operations."""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    details = db.Column(db.Text, nullable=True)  # JSON or text payload

    # Relationships
    user = db.relationship('User', back_populates='audit_logs')

    def __repr__(self):
        return f"<AuditLog action={self.action} user_id={self.user_id}>"
