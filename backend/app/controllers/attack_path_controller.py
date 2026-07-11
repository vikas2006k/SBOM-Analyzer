from app.services.attack_path_service import AttackPathService
from app.utils.response_helper import ResponseHelper
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class AttackPathController:
    """Controller handling graph intelligence and reachability attack path endpoints."""

    def __init__(self):
        self.attack_path_service = AttackPathService()

    def get_attack_paths(self, app_id):
        """Retrieve the graph analysis reports for an application."""
        try:
            report = self.attack_path_service.analyze_attack_paths(app_id)
            return ResponseHelper.success(report, "Application attack path intelligence analyzed successfully")
        except ValueError as ve:
            return ResponseHelper.error(str(ve), 404)
        except Exception as e:
            logger.error(f"Attack Path Analysis API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to analyze attack paths: {str(e)}", 500)
