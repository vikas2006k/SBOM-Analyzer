import os
from datetime import datetime
from app.database.connection import db
from app.models.sbom_upload import SBOMUpload
from app.models.application import Application
from app.models.library import Library
from app.models.dependency import Dependency
from app.utils.file_helper import FileHelper
from app.services.parser_service import ParserService
from app.services.dependency_service import DependencyService
from app.services.vulnerability_service import VulnerabilityService
from app.services.risk_service import RiskService
from app.repositories.base_repository import BaseRepository
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class SBOMService:
    """Service orchestrating SBOM file uploads, formats parsing, schema validation, and database ingestion."""

    def __init__(self):
        self.upload_repo = BaseRepository(SBOMUpload)
        self.app_repo = BaseRepository(Application)
        self.lib_repo = BaseRepository(Library)
        self.dep_repo = BaseRepository(Dependency)
        self.dep_service = DependencyService()
        self.vuln_service = VulnerabilityService()
        self.risk_service = RiskService()

    def get_all_uploads(self):
        """Retrieve all registered SBOMUpload metadata records."""
        return self.upload_repo.find_all()

    def get_upload_by_id(self, upload_id):
        """Retrieve single SBOMUpload record by ID."""
        return self.upload_repo.find_by_id(upload_id)

    def upload_sbom(self, application_id, file_payload, user_id):
        """Securely store uploaded SBOM file and record upload job details."""
        # 1. Verify target application exists
        app = self.app_repo.find_by_id(application_id)
        if not app:
            raise ValueError(f"Application profile with ID {application_id} does not exist")

        # 2. Stage file upload to destination path
        try:
            file_path, checksum = FileHelper.save_uploaded_file(file_payload)
        except ValueError as ve:
            raise ValueError(str(ve))
        except Exception as e:
            logger.error(f"File upload storage failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"File upload error: {str(e)}")

        # 3. Handle re-upload of same filename: soft-delete old COMPLETED record so
        #    re-analysis can be triggered freshly. This allows the user to upload
        #    the same file again to refresh/update the dependency data.
        existing_upload = SBOMUpload.query.filter_by(
            application_id=application_id,
            file_name=file_payload.filename,
            status='COMPLETED',
            is_deleted=False
        ).first()
        
        if existing_upload:
            logger.info(f"Re-upload detected for file: {file_payload.filename} — superseding previous upload ID {existing_upload.id}")
            existing_upload.is_deleted = True
            db.session.commit()

        # 4. Save upload record
        file_format = file_payload.filename.rsplit('.', 1)[1].lower()
        upload_record = self.upload_repo.create(
            application_id=application_id,
            file_name=file_payload.filename,
            file_format=file_format,
            file_path=file_path,  # Storing absolute path
            status='PENDING',
            uploaded_by=user_id
        )
        
        return {
            "upload_id": upload_record.id,
            "file_name": upload_record.file_name,
            "status": upload_record.status,
            "checksum": checksum
        }

    def parse_sbom(self, upload_id):
        """Trigger parsing and database ingestion pipeline for a pending SBOM upload."""
        upload = self.upload_repo.find_by_id(upload_id)
        if not upload:
            raise ValueError(f"Upload job ID {upload_id} not found")

        if upload.status in ('PROCESSING', 'COMPLETED'):
            return {"status": "already_processed", "upload_id": upload_id}

        # Update status to processing
        upload.status = 'PROCESSING'
        db.session.commit()

        try:
            # 1. Parse file structure
            parsed_data = ParserService.parse_sbom_file(upload.file_path, upload.file_format)
            
            # 2. Run validations
            validation_report = ParserService.validate_sbom(parsed_data)
            if not validation_report.get("valid"):
                # Mark upload as failed due to structural validation errors
                upload.status = 'FAILED'
                db.session.commit()
                return {
                    "status": "FAILED",
                    "upload_id": upload_id,
                    "validation_report": validation_report,
                    "errors": validation_report.get("errors")
                }

            # 3. Populate Application Version details (if default)
            app = self.app_repo.find_by_id(upload.application_id)
            if app.version == "1.0.0" and parsed_data.get("application_version") != "1.0.0":
                app.version = parsed_data.get("application_version")
                db.session.add(app)

            # 4. Ingest Libraries (bulk lookup / insert)
            libs_objs = {}
            for lib_data in parsed_data.get("libraries", []):
                name = lib_data.get("name")
                version = lib_data.get("version")
                ecosystem = lib_data.get("ecosystem", "npm")
                license_name = lib_data.get("license_name", "Unknown")

                # Check if library details already defined in database
                lib = Library.query.filter_by(
                    name=name,
                    version=version,
                    ecosystem=ecosystem,
                    is_deleted=False
                ).first()

                if not lib:
                    lib = self.lib_repo.create(
                        name=name,
                        version=version,
                        ecosystem=ecosystem,
                        license_name=license_name
                    )
                libs_objs[(name, version)] = lib.id

            # 5. Ingest Dependency graph edges
            # Delete old dependency edges for this application to overwrite with new uploads data
            Dependency.query.filter_by(application_id=upload.application_id).delete()

            for dep_data in parsed_data.get("dependencies", []):
                p_name = dep_data.get("parent_name")
                p_ver = dep_data.get("parent_version")
                c_name = dep_data.get("child_name")
                c_ver = dep_data.get("child_version")

                # Map parent ID (NULL if parent is root application)
                parent_lib_id = None
                if p_name != app.name or p_ver != app.version:
                    parent_lib_id = libs_objs.get((p_name, p_ver))
                    if not parent_lib_id:
                        # Fallback create parent if missing from libraries list
                        parent_lib = self.lib_repo.create(
                            name=p_name,
                            version=p_ver,
                            ecosystem="npm",
                            license_name="Unknown"
                        )
                        libs_objs[(p_name, p_ver)] = parent_lib.id
                        parent_lib_id = parent_lib.id

                child_lib_id = libs_objs.get((c_name, c_ver))
                if not child_lib_id:
                    # Fallback create child
                    child_lib = self.lib_repo.create(
                        name=c_name,
                        version=c_ver,
                        ecosystem="npm",
                        license_name="Unknown"
                    )
                    libs_objs[(c_name, c_ver)] = child_lib.id
                    child_lib_id = child_lib.id

                # Save edge link
                self.dep_repo.create(
                    application_id=upload.application_id,
                    parent_library_id=parent_lib_id,
                    child_library_id=child_lib_id,
                    depth=1,  # Temporary placeholder, calculated next
                    is_transitive=False
                )

            db.session.commit()

            # 6. Resolve Transitive Depths in DB using NetworkX
            self.dep_service.resolve_transitive_depths(upload.application_id)

            # 7. Audit vulnerability definitions matches & calculate composite risks
            self.vuln_service.match_vulnerabilities_for_application(upload.application_id)
            self.risk_service.calculate_risk_score(upload.application_id)

            # Mark upload execution as successful
            upload.status = 'COMPLETED'
            db.session.commit()

            return {
                "status": "COMPLETED",
                "upload_id": upload_id,
                "libraries_imported": len(libs_objs),
                "validation_report": validation_report
            }

        except Exception as ex:
            logger.error(f"SBOM Parsing Ingestion failed: {str(ex)}", exc_info=True)
            upload.status = 'FAILED'
            db.session.commit()
            raise RuntimeError(f"SBOM Parsing error: {str(ex)}")
