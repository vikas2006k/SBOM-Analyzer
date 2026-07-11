from flask import send_file, g
from app.services.report_service import ReportService
from app.utils.response_helper import ResponseHelper
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class ReportController:
    """Controller exporting executive PDF reports and developer patches list CSVs."""

    def __init__(self):
        self.report_service = ReportService()

    def download_pdf(self, app_id):
        """Compile and send executive report PDF file."""
        try:
            user_id = g.current_user.id if hasattr(g, 'current_user') else 1
            result = self.report_service.generate_executive_pdf(app_id, user_id)
            return send_file(
                result["absolute_path"],
                mimetype='application/pdf',
                as_attachment=True,
                download_name=result["filename"]
            )
        except ValueError as ve:
            return ResponseHelper.error(str(ve), 404)
        except Exception as e:
            logger.error(f"Generate PDF API failed: {str(e)}", exc_info=True)
            return ResponseHelper.error(f"Failed to generate PDF document: {str(e)}", 500)

    def download_csv(self, app_id):
        """Compile and send developer actions patches list CSV file."""
        try:
            user_id = g.current_user.id if hasattr(g, 'current_user') else 1
            result = self.report_service.generate_developer_csv(app_id, user_id)
            return send_file(
                result["absolute_path"],
                mimetype='text/csv',
                as_attachment=True,
                download_name=result["filename"]
            )
        except ValueError as ve:
            return ResponseHelper.error(str(ve), 404)
        except Exception as e:
            logger.error(f"Generate CSV API failed: {str(e)}", exc_info=True)
            return ResponseHelper.error(f"Failed to generate CSV export file: {str(e)}", 500)
