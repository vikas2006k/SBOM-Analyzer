from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class LicenseRule(db.Model, TimestampMixin, SoftDeleteMixin):
    """LicenseRule model defining risk level rules for license types."""
    __tablename__ = 'license_rules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    license_category = db.Column(db.String(50), unique=True, nullable=False, index=True)
    commercial_allowed = db.Column(db.Boolean, default=True, nullable=False)
    proprietary_linkable = db.Column(db.Boolean, default=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<LicenseRule category={self.license_category}>"
