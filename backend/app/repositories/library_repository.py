from app.models.library import Library
from app.repositories.base_repository import BaseRepository

class LibraryRepository(BaseRepository):
    """Repository handling custom operations for the Library model."""
    def __init__(self):
        super().__init__(Library)

    def find_by_name_and_version(self, name, version, ecosystem):
        """Find a specific library version reference."""
        return Library.query.filter(
            Library.name == name,
            Library.version == version,
            Library.ecosystem == ecosystem,
            Library.is_deleted == False
        ).first()

    def search_libraries(self, query_str, ecosystem=None, page=1, per_page=10):
        """Search libraries by name, ecosystem, or license."""
        query = Library.query.filter(Library.is_deleted == False)
        if query_str:
            query = query.filter(Library.name.ilike(f"%{query_str}%"))
        if ecosystem:
            query = query.filter(Library.ecosystem == ecosystem)
        return self.paginate(query, page, per_page)
