from sqlalchemy.sql import func
from app.database.connection import db
from app.models.application import Application
from app.models.library import Library
from app.models.vulnerability import Vulnerability
from app.models.dependency import Dependency
from app.models.risk import RiskScore
from app.models.license import License
from app.models.maintenance import MaintenanceRecord
from app.models.copilot import AIConversation
from app.services.risk_service import RiskService
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class DashboardService:
    """Service compiling executive KPIs dashboards and global multi-entity searches."""

    def __init__(self):
        self.risk_service = RiskService()

    def get_executive_metrics(self):
        """Compile aggregated security supply chain metrics across the workspace."""
        logger.info("Compiling executive dashboard KPI metrics...")
        
        total_apps = Application.query.filter_by(is_deleted=False).count()
        total_libs = Library.query.filter_by(is_deleted=False).count()
        total_cves = Vulnerability.query.filter_by(is_deleted=False).count()
        
        # Calculate active vulnerabilities
        active_cve_count = db.session.query(func.distinct(Vulnerability.id))\
            .join(Library.vulnerabilities)\
            .join(Dependency, Dependency.child_library_id == Library.id)\
            .filter(Dependency.is_deleted == False)\
            .count()
            
        # Risk scores averages
        avg_risk_row = db.session.query(func.avg(RiskScore.overall_score))\
            .filter(RiskScore.is_deleted == False).first()
        avg_risk = float(avg_risk_row[0]) if avg_risk_row and avg_risk_row[0] is not None else 0.0
        
        # Severity distribution of active vulnerabilities
        sev_counts = db.session.query(Vulnerability.severity, func.count(func.distinct(Vulnerability.id)))\
            .join(Library.vulnerabilities)\
            .join(Dependency, Dependency.child_library_id == Library.id)\
            .filter(Dependency.is_deleted == False)\
            .group_by(Vulnerability.severity).all()
            
        severity_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
        for sev, count in sev_counts:
            if sev in severity_dist:
                severity_dist[sev] = count
                
        # License distribution
        lic_counts = db.session.query(Library.license_name, func.count(Library.id))\
            .filter(Library.is_deleted == False)\
            .group_by(Library.license_name).all()
        license_dist = {lic_name or "Unknown": count for lic_name, count in lic_counts if count > 0}
        
        # Application list with summary status
        apps = Application.query.filter_by(is_deleted=False).all()
        apps_summary = []
        for app in apps:
            risk_score = RiskScore.query.filter_by(application_id=app.id).first()
            score_val = float(risk_score.overall_score) if risk_score else 0.0
            
            # Count vulnerabilities for this app
            app_cves = db.session.query(func.count(func.distinct(Vulnerability.id)))\
                .join(Library.vulnerabilities)\
                .join(Dependency, Dependency.child_library_id == Library.id)\
                .filter(Dependency.application_id == app.id, Dependency.is_deleted == False)\
                .scalar() or 0
                
            apps_summary.append({
                "id": app.id,
                "name": app.name,
                "version": app.version,
                "business_criticality": app.business_criticality,
                "risk_score": score_val,
                "risk_severity": self.risk_service.get_risk_severity(score_val),
                "vulnerabilities_count": app_cves
            })
            
        return {
            "total_applications": total_apps,
            "total_libraries": total_libs,
            "vulnerabilities_catalog": total_cves,
            "active_vulnerabilities": active_cve_count,
            "average_risk_score": round(avg_risk, 2),
            "average_risk_severity": self.risk_service.get_risk_severity(avg_risk),
            "severity_distribution": severity_dist,
            "license_distribution": license_dist,
            "applications_status": apps_summary
        }

    def global_search(self, search_query):
        """Execute cross-entity text search across the database."""
        logger.info(f"Executing global search for query: '{search_query}'")
        if not search_query or not isinstance(search_query, str):
            return {"applications": [], "libraries": [], "vulnerabilities": [], "conversations": []}
            
        term = f"%{search_query}%"
        
        # Search applications
        apps = Application.query.filter(
            (Application.name.ilike(term)) | 
            (Application.description.ilike(term))
        ).filter_by(is_deleted=False).all()
        
        # Search libraries
        libs = Library.query.filter(
            (Library.name.ilike(term)) | 
            (Library.license_name.ilike(term)) | 
            (Library.ecosystem.ilike(term))
        ).filter_by(is_deleted=False).all()
        
        # Search vulnerabilities
        cves = Vulnerability.query.filter(
            (Vulnerability.cve_id.ilike(term)) | 
            (Vulnerability.description.ilike(term))
        ).filter_by(is_deleted=False).all()
        
        # Search AI chats
        chats = AIConversation.query.filter(
            AIConversation.message_history.ilike(term)
        ).filter_by(is_deleted=False).all()
        
        return {
            "applications": [{
                "id": a.id,
                "name": a.name,
                "version": a.version,
                "description": a.description,
                "business_criticality": a.business_criticality
            } for a in apps],
            "libraries": [{
                "id": l.id,
                "name": l.name,
                "version": l.version,
                "ecosystem": l.ecosystem,
                "license": l.license_name
            } for l in libs],
            "vulnerabilities": [{
                "id": v.id,
                "cve_id": v.cve_id,
                "cvss_score": float(v.cvss_score),
                "severity": v.severity,
                "description": v.description[:120] + "..." if len(v.description) > 120 else v.description
            } for v in cves],
            "conversations": [{
                "id": c.id,
                "application_id": c.application_id,
                "application_name": c.application.name if c.application else "Unknown"
            } for c in chats]
        }
