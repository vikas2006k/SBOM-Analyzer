from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class Application(db.Model, TimestampMixin, SoftDeleteMixin):
    """Application model representing software projects under analysis."""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    version = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=True)
    business_criticality = db.Column(db.Enum('Low', 'Medium', 'High', 'Critical', name='business_criticality_types'), default='Medium', nullable=False)

    # Relationships
    uploads = db.relationship('SBOMUpload', back_populates='application', cascade="all, delete-orphan")
    dependency_edges = db.relationship('Dependency', back_populates='application', cascade="all, delete-orphan")
    risk_scores = db.relationship('RiskScore', back_populates='application', cascade="all, delete-orphan")
    reports = db.relationship('AnalysisReport', back_populates='application', cascade="all, delete-orphan")
    conversations = db.relationship('AIConversation', back_populates='application', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Application {self.name} v{self.version}>"
