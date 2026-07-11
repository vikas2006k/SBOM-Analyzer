from app.models.dependency import Dependency
from app.repositories.base_repository import BaseRepository

class DependencyRepository(BaseRepository):
    """Repository handling operations on dependency graph edges."""
    def __init__(self):
        super().__init__(Dependency)

    def find_edges_by_application(self, application_id):
        """Retrieve all active dependency relationships for an application."""
        return Dependency.query.filter(
            Dependency.application_id == application_id,
            Dependency.is_deleted == False
        ).all()

    def find_root_dependencies(self, application_id):
        """Find direct (root) dependencies of an application (parent_library_id is NULL)."""
        return Dependency.query.filter(
            Dependency.application_id == application_id,
            Dependency.parent_library_id.is_(None),
            Dependency.is_deleted == False
        ).all()

    def find_transitive_dependencies(self, application_id):
        """Find transitive dependencies (depth > 1)."""
        return Dependency.query.filter(
            Dependency.application_id == application_id,
            Dependency.depth > 1,
            Dependency.is_deleted == False
        ).all()
