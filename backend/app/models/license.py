from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class License(db.Model, TimestampMixin, SoftDeleteMixin):
    """License model representing dependency licenses."""
    __tablename__ = 'licenses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spdx_identifier = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.Enum('Permissive', 'Weak-Copyleft', 'Copyleft', 'Proprietary', 'Unknown', name='license_categories'), default='Unknown', nullable=False)

    def __repr__(self):
        return f"<License {self.spdx_identifier}>"
