from app.models.application import Application
from app.repositories.base_repository import BaseRepository

class ApplicationRepository(BaseRepository):
    """Repository handling custom operations for the Application model."""
    def __init__(self):
        super().__init__(Application)

    def find_by_name(self, name, include_deleted=False):
        """Find application profiles by name."""
        query = Application.query.filter(Application.name == name)
        if not include_deleted:
            query = query.filter(Application.is_deleted == False)
        return query.all()

    def search_applications(self, query_str, criticality=None, page=1, per_page=10):
        """Search application profiles by name or description."""
        query = Application.query.filter(Application.is_deleted == False)
        if query_str:
            query = query.filter(
                (Application.name.ilike(f"%{query_str}%")) |
                (Application.description.ilike(f"%{query_str}%"))
            )
        if criticality:
            query = query.filter(Application.business_criticality == criticality)
        return self.paginate(query, page, per_page)
