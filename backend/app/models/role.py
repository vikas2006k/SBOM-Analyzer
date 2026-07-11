from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class Role(db.Model, TimestampMixin, SoftDeleteMixin):
    """Role model representing access levels."""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    permissions = db.Column(db.Text, nullable=False, default="[]")  # JSON String of permissions

    # Relationships
    users = db.relationship('User', back_populates='role', lazy=True)

    def __repr__(self):
        return f"<Role {self.name}>"
