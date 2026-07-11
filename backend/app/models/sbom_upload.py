from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class SBOMUpload(db.Model, TimestampMixin, SoftDeleteMixin):
    """SBOMUpload model representing uploaded files and processing state."""
    __tablename__ = 'sbom_uploads'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_format = db.Column(db.String(10), nullable=False)  # 'json', 'csv'
    file_path = db.Column(db.String(500), nullable=False)
    status = db.Column(db.Enum('PENDING', 'PROCESSING', 'FAILED', 'COMPLETED', name='upload_status_types'), default='PENDING', nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    application = db.relationship('Application', back_populates='uploads')
    uploader = db.relationship('User', back_populates='uploads')

    def __repr__(self):
        return f"<SBOMUpload id={self.id} file={self.file_name} status={self.status}>"
