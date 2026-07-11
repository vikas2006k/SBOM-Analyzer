from app.database.connection import db
from app.models.base import TimestampMixin, SoftDeleteMixin

class AnalysisReport(db.Model, TimestampMixin, SoftDeleteMixin):
    """AnalysisReport model representing generated risk audit documents."""
    __tablename__ = 'analysis_reports'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, index=True)
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    format = db.Column(db.Enum('PDF', 'CSV', name='report_format_types'), nullable=False)
    report_type = db.Column(db.Enum('Executive', 'Developer', name='report_output_types'), default='Executive', nullable=False)

    # Relationships
    application = db.relationship('Application', back_populates='reports')
    generator = db.relationship('User', back_populates='reports')

    def __repr__(self):
        return f"<AnalysisReport id={self.id} type={self.report_type} format={self.format}>"
