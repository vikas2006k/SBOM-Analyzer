from flask import request
from app.services.dashboard_service import DashboardService
from app.utils.response_helper import ResponseHelper
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class DashboardController:
    """Controller compiling general dashboard analytics metrics and orchestrating global search."""

    def __init__(self):
        self.dashboard_service = DashboardService()

    def get_summary(self):
        """Retrieve overall system analytics KPI statistics."""
        try:
            app_id = request.args.get("application_id")
            app_id_val = int(app_id) if app_id else None
            summary = self.dashboard_service.get_executive_metrics(app_id_val)
            return ResponseHelper.success(summary, "Dashboard summary statistics compiled successfully")
        except Exception as e:
            logger.error(f"Dashboard Summary API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to compile dashboard summary: {str(e)}", 500)

    def global_search(self):
        """Execute text search query across all workspace databases tables."""
        try:
            query = request.args.get("query", "").strip()
            if not query:
                return ResponseHelper.error("Missing search query string parameter", 400)
                
            results = self.dashboard_service.global_search(query)
            return ResponseHelper.success(results, f"Global search queries executed successfully for '{query}'")
        except Exception as e:
            logger.error(f"Global Search API failed: {str(e)}")
            return ResponseHelper.error(f"Unified search failed: {str(e)}", 500)
