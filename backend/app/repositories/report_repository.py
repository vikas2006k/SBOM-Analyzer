from app.models.report import AnalysisReport
from app.repositories.base_repository import BaseRepository

class ReportRepository(BaseRepository):
    """Repository handling custom operations for the AnalysisReport model."""
    def __init__(self):
        super().__init__(AnalysisReport)

    def find_reports_by_application(self, application_id, page=1, per_page=10):
        """Retrieve all active reports for an application with pagination."""
        query = AnalysisReport.query.filter(
            AnalysisReport.application_id == application_id,
            AnalysisReport.is_deleted == False
        ).order_by(AnalysisReport.created_at.desc())
        return self.paginate(query, page, per_page)
