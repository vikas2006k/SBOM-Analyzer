from app.database.connection import db

class BaseRepository:
    """Generic base repository for common database CRUD operations."""
    def __init__(self, model):
        self.model = model

    def create(self, **kwargs):
        """Create a new model record."""
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, instance, **kwargs):
        """Update fields on an existing model record."""
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.session.commit()
        return instance

    def delete(self, instance, soft=True):
        """Delete a record (supports soft delete if model supports it)."""
        if soft and hasattr(instance, 'soft_delete'):
            instance.soft_delete()
        else:
            db.session.delete(instance)
        db.session.commit()
        return True

    def find_by_id(self, id_val, include_deleted=False):
        """Find a single record by ID."""
        query = db.session.query(self.model).filter(self.model.id == id_val)
        if hasattr(self.model, 'is_deleted') and not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        return query.first()

    def find_all(self, include_deleted=False):
        """Find all records."""
        query = db.session.query(self.model)
        if hasattr(self.model, 'is_deleted') and not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        return query.all()

    def paginate(self, query=None, page=1, per_page=10):
        """Paginate database queries."""
        if query is None:
            query = db.session.query(self.model)
            if hasattr(self.model, 'is_deleted'):
                query = query.filter(self.model.is_deleted == False)
        
        paginated_obj = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            "items": paginated_obj.items,
            "total_items": paginated_obj.total,
            "current_page": paginated_obj.page,
            "total_pages": paginated_obj.pages,
            "per_page": paginated_obj.per_page
        }
