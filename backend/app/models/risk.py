from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class RiskScore(db.Model, TimestampMixin, SoftDeleteMixin):
    """RiskScore model holding aggregated metrics output."""
    __tablename__ = 'risk_scores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, index=True)
    overall_score = db.Column(db.Numeric(5, 2), nullable=False)
    cvss_subscore = db.Column(db.Numeric(5, 2), nullable=False)
    license_subscore = db.Column(db.Numeric(5, 2), nullable=False)
    maintenance_subscore = db.Column(db.Numeric(5, 2), nullable=False)

    # Relationships
    application = db.relationship('Application', back_populates='risk_scores')
    factors = db.relationship('RiskFactor', back_populates='risk_score', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RiskScore app_id={self.application_id} overall={self.overall_score}>"

class RiskFactor(db.Model, TimestampMixin, SoftDeleteMixin):
    """RiskFactor model storing singular risk contributions."""
    __tablename__ = 'risk_factors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    risk_score_id = db.Column(db.Integer, db.ForeignKey('risk_scores.id'), nullable=False, index=True)
    factor_type = db.Column(db.Enum('CVE', 'License', 'Maintenance', 'Architecture', name='risk_factor_types'), nullable=False)
    impact_level = db.Column(db.Enum('Low', 'Medium', 'High', 'Critical', name='impact_levels'), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Relationships
    risk_score = db.relationship('RiskScore', back_populates='factors')

    def __repr__(self):
        return f"<RiskFactor type={self.factor_type} impact={self.impact_level}>"
