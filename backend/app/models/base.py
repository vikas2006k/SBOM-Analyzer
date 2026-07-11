from datetime import datetime
from app.database.connection import db

class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models."""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SoftDeleteMixin:
    """Mixin to add soft delete support to models."""
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        """Soft delete model record."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        db.session.add(self)

    def restore(self):
        """Restore soft deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        db.session.add(self)
