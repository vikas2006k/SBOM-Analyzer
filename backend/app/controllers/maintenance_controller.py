from app.services.maintenance_service import MaintenanceService
from app.utils.response_helper import ResponseHelper
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class MaintenanceController:
    """Controller returning maintenance metrics for libraries and applications."""

    def __init__(self):
        self.maintenance_service = MaintenanceService()

    def get_application_maintenance(self, app_id):
        """Retrieve maintenance score breakdown details for a given application."""
        try:
            report = self.maintenance_service.check_maintenance_health(app_id)
            return ResponseHelper.success(report, "Application maintenance intelligence summary retrieved successfully")
        except ValueError as ve:
            return ResponseHelper.error(str(ve), 404)
        except Exception as e:
            logger.error(f"Maintenance Intelligence API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to fetch maintenance health details: {str(e)}", 500)
