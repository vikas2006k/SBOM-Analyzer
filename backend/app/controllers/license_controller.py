from flask import request
from app.services.license_service import LicenseService
from app.models.license_rule import LicenseRule
from app.database.connection import db
from app.utils.response_helper import ResponseHelper
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class LicenseController:
    """Controller handling license compliance auditing and configuration rules."""

    def __init__(self):
        self.license_service = LicenseService()

    def audit_application_licenses(self, app_id):
        """Audit the compliance status of dependencies licenses for a given project."""
        try:
            report = self.license_service.audit_licenses(app_id)
            return ResponseHelper.success(report, "Application license audit executed successfully")
        except ValueError as ve:
            return ResponseHelper.error(str(ve), 404)
        except Exception as e:
            logger.error(f"License Audit API failed: {str(e)}")
            return ResponseHelper.error(f"License audit failed: {str(e)}", 500)

    def get_license_rules(self):
        """Retrieve list of defined license policy rules."""
        try:
            rules = LicenseRule.query.filter_by(is_deleted=False).all()
            results = []
            for r in rules:
                results.append({
                    "id": r.id,
                    "license_category": r.license_category,
                    "commercial_allowed": r.commercial_allowed,
                    "proprietary_linkable": r.proprietary_linkable,
                    "description": r.description
                })
            return ResponseHelper.success(results, "License compliance rules retrieved successfully")
        except Exception as e:
            logger.error(f"Get License Rules API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to fetch license rules: {str(e)}", 500)

    def update_license_rule(self):
        """Update a specific license policy rule parameters (admin/security only)."""
        try:
            data = request.get_json() or {}
            category = data.get("license_category")
            commercial_allowed = data.get("commercial_allowed")
            proprietary_linkable = data.get("proprietary_linkable")
            
            if not category:
                return ResponseHelper.error("Missing required parameter: license_category", 400)
                
            rule = LicenseRule.query.filter_by(license_category=category).first()
            if not rule:
                return ResponseHelper.error(f"Rule for category '{category}' not found", 404)
                
            if commercial_allowed is not None:
                rule.commercial_allowed = bool(commercial_allowed)
            if proprietary_linkable is not None:
                rule.proprietary_linkable = bool(proprietary_linkable)
                
            db.session.commit()
            
            return ResponseHelper.success({
                "id": rule.id,
                "license_category": rule.license_category,
                "commercial_allowed": rule.commercial_allowed,
                "proprietary_linkable": rule.proprietary_linkable,
                "description": rule.description
            }, f"License policy rule for category '{category}' updated successfully")
            
        except Exception as e:
            logger.error(f"Update License Rule API failed: {str(e)}")
            return ResponseHelper.error(f"Failed to update license policy rule: {str(e)}", 500)
