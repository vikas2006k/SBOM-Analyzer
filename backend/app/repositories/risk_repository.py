from app.models.risk import RiskScore, RiskFactor
from app.repositories.base_repository import BaseRepository

class RiskRepository(BaseRepository):
    """Repository handling custom operations for RiskScore and RiskFactor models."""
    def __init__(self):
        super().__init__(RiskScore)

    def find_latest_score_by_application(self, application_id):
        """Retrieve the most recent calculated RiskScore for an application."""
        return RiskScore.query.filter(
            RiskScore.application_id == application_id,
            RiskScore.is_deleted == False
        ).order_by(RiskScore.created_at.desc()).first()

    def find_factors_by_score_id(self, score_id):
        """Get all risk contribution factors details for a given score."""
        return RiskFactor.query.filter(
            RiskFactor.risk_score_id == score_id,
            RiskFactor.is_deleted == False
        ).all()
