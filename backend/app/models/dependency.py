from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class Dependency(db.Model, TimestampMixin, SoftDeleteMixin):
    """Dependency model representing the directed dependency graph edges."""
    __tablename__ = 'dependency_graph'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, index=True)
    parent_library_id = db.Column(db.Integer, db.ForeignKey('libraries.id'), nullable=True, index=True)  # Null if root dependency
    child_library_id = db.Column(db.Integer, db.ForeignKey('libraries.id'), nullable=False, index=True)
    depth = db.Column(db.Integer, nullable=False, default=1)
    is_transitive = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    application = db.relationship('Application', back_populates='dependency_edges')
    parent_library = db.relationship('Library', foreign_keys=[parent_library_id])
    child_library = db.relationship('Library', foreign_keys=[child_library_id])

    def __repr__(self):
        return f"<Dependency app_id={self.application_id} parent={self.parent_library_id} child={self.child_library_id} depth={self.depth}>"
