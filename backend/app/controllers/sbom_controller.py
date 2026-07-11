from flask import request, g
from app.services.sbom_service import SBOMService
from app.utils.response_helper import ResponseHelper
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class SBOMController:
    """Controller handling SBOM file uploads and processing endpoints."""

    def __init__(self):
        self.sbom_service = SBOMService()

    def upload_sbom(self):
        """Handle POST request uploading SBOM files."""
        try:
            # Validate input parameter application_id
            app_id = request.form.get("application_id")
            if not app_id:
                return ResponseHelper.error("Missing required parameter: application_id", 400)

            # Check if file exists in payload
            if 'file' not in request.files:
                return ResponseHelper.error("No file payload part in the request", 400)
                
            file = request.files['file']
            if file.filename == '':
                return ResponseHelper.error("No file selected for uploading", 400)

            # Extract user identity from request context (mock default if missing)
            user_id = getattr(g, 'current_user', None)
            user_id_val = user_id.id if user_id else 1 # Fallback to admin user

            result = self.sbom_service.upload_sbom(int(app_id), file, user_id_val)
            return ResponseHelper.success(result, "SBOM uploaded and staged successfully", 201)

        except ValueError as ve:
            return ResponseHelper.error(str(ve), 400)
        except Exception as e:
            logger.error(f"Upload API failed: {str(e)}")
            return ResponseHelper.error(f"Internal Upload Error: {str(e)}", 500)

    def parse_sbom(self, upload_id):
        """Handle POST request executing SBOM parsing jobs."""
        try:
            result = self.sbom_service.parse_sbom(upload_id)
            if result.get("status") == "FAILED":
                return ResponseHelper.error("SBOM validation failed", 400, details=result)
            return ResponseHelper.success(result, "SBOM parsed and ingested successfully")
        except ValueError as ve:
            return ResponseHelper.error(str(ve), 400)
        except Exception as e:
            logger.error(f"Parse API failed: {str(e)}")
            return ResponseHelper.error(f"Parsing Ingestion Error: {str(e)}", 500)

    def list_uploads(self):
        """Handle GET request listing uploads records."""
        try:
            uploads = self.sbom_service.get_all_uploads()
            uploads_list = []
            for up in uploads:
                uploads_list.append({
                    "id": up.id,
                    "application_id": up.application_id,
                    "file_name": up.file_name,
                    "file_format": up.file_format,
                    "status": up.status,
                    "uploaded_by": up.uploaded_by,
                    "created_at": up.created_at.isoformat() if up.created_at else None
                })
            return ResponseHelper.success(uploads_list, "Uploads retrieved successfully")
        except Exception as e:
            logger.error(f"List Uploads API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to fetch uploads: {str(e)}", 500)
