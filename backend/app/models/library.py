from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

# Association table for Library <=> Vulnerability (Many-to-Many)
library_vulnerabilities = db.Table(
    'library_vulnerabilities',
    db.Column('library_id', db.Integer, db.ForeignKey('libraries.id', ondelete='CASCADE'), primary_key=True),
    db.Column('vulnerability_id', db.Integer, db.ForeignKey('vulnerabilities.id', ondelete='CASCADE'), primary_key=True)
)

class Library(db.Model, TimestampMixin, SoftDeleteMixin):
    """Library model representing an extracted SBOM dependency version."""
    __tablename__ = 'libraries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    version = db.Column(db.String(50), nullable=False, index=True)
    ecosystem = db.Column(db.String(20), nullable=False)  # 'npm', 'pypi', 'maven', etc.
    license_name = db.Column(db.String(100), nullable=True)

    # Relationships
    vulnerabilities = db.relationship('Vulnerability', secondary=library_vulnerabilities, back_populates='libraries')
    maintenance_records = db.relationship('MaintenanceRecord', back_populates='library', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Library {self.name} v{self.version} ({self.ecosystem})>"
