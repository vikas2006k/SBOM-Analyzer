from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class MaintenanceRecord(db.Model, TimestampMixin, SoftDeleteMixin):
    """MaintenanceRecord model tracking dependency project activity state."""
    __tablename__ = 'maintenance_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    library_id = db.Column(db.Integer, db.ForeignKey('libraries.id'), nullable=False, unique=True, index=True)
    last_updated = db.Column(db.DateTime, nullable=False)
    commit_frequency_annual = db.Column(db.Integer, default=0, nullable=False)
    open_issues_count = db.Column(db.Integer, default=0, nullable=False)
    bus_factor = db.Column(db.Integer, default=1, nullable=False)
    is_deprecated = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    library = db.relationship('Library', back_populates='maintenance_records')

    def __repr__(self):
        return f"<MaintenanceRecord library_id={self.library_id} is_deprecated={self.is_deprecated}>"
