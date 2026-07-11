from app.services.risk_service import RiskService
from app.utils.response_helper import ResponseHelper
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class RiskController:
    """Controller handling composite risk reports calculations and scoring retrieval."""

    def __init__(self):
        self.risk_service = RiskService()

    def get_application_risk(self, app_id):
        """Retrieve the latest composite risk score profile for an application."""
        try:
            report = self.risk_service.get_latest_risk_score(app_id)
            return ResponseHelper.success(report, "Application risk intelligence report retrieved successfully")
        except ValueError as ve:
            return ResponseHelper.error(str(ve), 404)
        except Exception as e:
            logger.error(f"Get Risk Report API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to fetch risk report details: {str(e)}", 500)

    def calculate_application_risk(self, app_id):
        """Force recalculation of the composite risk scores for a given project."""
        try:
            report = self.risk_service.calculate_risk_score(app_id)
            return ResponseHelper.success(report, "Application risk profile recalculated successfully")
        except ValueError as ve:
            return ResponseHelper.error(str(ve), 404)
        except Exception as e:
            logger.error(f"Recalculate Risk Score API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to recalculate composite risk scores: {str(e)}", 500)
