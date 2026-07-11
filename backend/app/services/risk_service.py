from decimal import Decimal
from app.database.connection import db
from app.models.application import Application
from app.models.risk import RiskScore, RiskFactor
from app.services.vulnerability_service import VulnerabilityService
from app.services.license_service import LicenseService
from app.services.maintenance_service import MaintenanceService
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class RiskService:
    """Service executing multi-factor composite risk engine calculations."""

    def __init__(self):
        self.vuln_service = VulnerabilityService()
        self.license_service = LicenseService()
        self.maint_service = MaintenanceService()

    def get_risk_severity(self, score):
        """Map score 0-100 to risk level category."""
        score_val = float(score)
        if score_val >= 75.0:
            return "Critical"
        elif score_val >= 50.0:
            return "High"
        elif score_val >= 25.0:
            return "Medium"
        else:
            return "Low"

    def calculate_risk_score(self, application_id):
        """Execute risk score aggregation calculations and persist logs."""
        logger.info(f"Triggering composite risk score calculations for application {application_id}")
        
        app = db.session.get(Application, application_id)
        if not app:
            raise ValueError(f"Application with ID {application_id} not found")
            
        # 1. Audit components
        vulns = self.vuln_service.get_vulnerabilities_by_application(application_id)
        license_audit = self.license_service.audit_licenses(application_id)
        maint_audit = self.maint_service.check_maintenance_health(application_id)
        
        # 2. CVSS Subscore calculation
        max_cvss = max([v["cvss_score"] for v in vulns]) if vulns else 0.0
        cvss_risk = min(100.0, max_cvss * 10)
        
        # 3. License Subscore calculation (invert license score)
        license_risk = max(0.0, 100.0 - license_audit["license_score"])
        
        # 4. Maintenance Subscore calculation (invert maintenance score)
        maint_risk = max(0.0, 100.0 - maint_audit["average_maintenance_score"])
        
        # 5. Architecture/Depth Risk
        # Direct vulnerability has higher risk impact than transitive
        has_direct_vuln = any(not v["exploitability"].get("is_transitive", False) and v["cvss_score"] >= 7.0 for v in vulns)
        depth_risk = 100.0 if has_direct_vuln else (40.0 if vulns else 0.0)
        
        # 6. Weight Aggregator
        raw_score = (cvss_risk * 0.45) + (license_risk * 0.25) + (maint_risk * 0.20) + (depth_risk * 0.10)
        
        # 7. Apply Business Criticality multiplier
        multipliers = {
            "Low": 0.8,
            "Medium": 1.0,
            "High": 1.1,
            "Critical": 1.25
        }
        mult = multipliers.get(app.business_criticality, 1.0)
        overall_score = min(100.0, max(0.0, raw_score * mult))
        
        # Determine Severity
        severity = self.get_risk_severity(overall_score)
        
        # 8. Create or update RiskScore in DB
        risk_score = RiskScore.query.filter_by(application_id=application_id).first()
        if risk_score:
            # Delete existing factors
            RiskFactor.query.filter_by(risk_score_id=risk_score.id).delete()
            risk_score.overall_score = Decimal(str(round(overall_score, 2)))
            risk_score.cvss_subscore = Decimal(str(round(cvss_risk, 2)))
            risk_score.license_subscore = Decimal(str(round(license_risk, 2)))
            risk_score.maintenance_subscore = Decimal(str(round(maint_risk, 2)))
        else:
            risk_score = RiskScore(
                application_id=application_id,
                overall_score=Decimal(str(round(overall_score, 2))),
                cvss_subscore=Decimal(str(round(cvss_risk, 2))),
                license_subscore=Decimal(str(round(license_risk, 2))),
                maintenance_subscore=Decimal(str(round(maint_risk, 2)))
            )
            db.session.add(risk_score)
            db.session.commit()
            
        # 9. Generate granular RiskFactors and add explanations
        factors_created = []
        explanation_clauses = []
        
        # Vulnerability factor
        if vulns:
            impact = "Critical" if max_cvss >= 9.0 else ("High" if max_cvss >= 7.0 else "Medium")
            vuln_desc = f"Application dependencies contain {len(vulns)} vulnerability CVEs. Highest CVSS score is {max_cvss}."
            factor = RiskFactor(
                risk_score_id=risk_score.id,
                factor_type="CVE",
                impact_level=impact,
                description=vuln_desc
            )
            db.session.add(factor)
            factors_created.append(factor)
            explanation_clauses.append(f"a max CVSS vulnerability score of {max_cvss} ({impact})")
            
        # License factor
        if license_audit["conflicts_count"] > 0:
            factor = RiskFactor(
                risk_score_id=risk_score.id,
                factor_type="License",
                impact_level="High",
                description=f"Detected {license_audit['conflicts_count']} copyleft compliance conflicts."
            )
            db.session.add(factor)
            factors_created.append(factor)
            explanation_clauses.append(f"{license_audit['conflicts_count']} license conflicts violating policy rules")
            
        # Maintenance factor
        if maint_audit["average_maintenance_score"] < 70.0:
            maint_impact = "High" if maint_audit["average_maintenance_score"] < 50.0 else "Medium"
            factor = RiskFactor(
                risk_score_id=risk_score.id,
                factor_type="Maintenance",
                impact_level=maint_impact,
                description=f"Average maintenance health is low ({maint_audit['average_maintenance_score']}/100) indicating abandoned or deprecated dependencies."
            )
            db.session.add(factor)
            factors_created.append(factor)
            explanation_clauses.append(f"deprecated or inactive dependencies (maintenance score: {maint_audit['average_maintenance_score']})")
            
        # Architecture factor
        if has_direct_vuln:
            factor = RiskFactor(
                risk_score_id=risk_score.id,
                factor_type="Architecture",
                impact_level="High",
                description="Direct dependencies contain critical vulnerabilities, offering direct threat exposure pathways."
            )
            db.session.add(factor)
            factors_created.append(factor)
            explanation_clauses.append("direct vulnerabilities in primary software components")
            
        db.session.commit()
        
        # Build explanation text
        if explanation_clauses:
            clause_str = ", ".join(explanation_clauses[:-1])
            if len(explanation_clauses) > 1:
                clause_str += f", and {explanation_clauses[-1]}"
            else:
                clause_str = explanation_clauses[0]
                
            explanation = (
                f"The overall risk score of {round(overall_score, 1)} ({severity}) for {app.name} is primarily driven by {clause_str}. "
                f"The application business criticality multiplier of {mult}x has adjusted this score accordingly."
            )
        else:
            explanation = (
                f"The project is healthy with an overall risk score of {round(overall_score, 1)} ({severity}). "
                "No critical CVEs, copyleft license violations, or obsolete library dependencies were detected."
            )
            
        return {
            "application_id": application_id,
            "overall_score": round(overall_score, 2),
            "severity": severity,
            "sub_scores": {
                "cvss_risk": round(cvss_risk, 2),
                "license_risk": round(license_risk, 2),
                "maintenance_risk": round(maint_risk, 2),
                "architecture_risk": round(depth_risk, 2)
            },
            "business_multiplier": mult,
            "explanation": explanation,
            "factors": [{
                "type": f.factor_type,
                "impact": f.impact_level,
                "description": f.description
            } for f in factors_created]
        }

    def get_latest_risk_score(self, application_id):
        """Retrieve the latest risk calculations from database."""
        risk_score = RiskScore.query.filter_by(application_id=application_id, is_deleted=False).first()
        if not risk_score:
            # Trigger calculation if none exists
            return self.calculate_risk_score(application_id)
            
        factors = RiskFactor.query.filter_by(risk_score_id=risk_score.id, is_deleted=False).all()
        severity = self.get_risk_severity(risk_score.overall_score)
        
        # Re-generate description for convenience
        app = db.session.get(Application, application_id)
        mult = 1.0
        if app:
            multipliers = {"Low": 0.8, "Medium": 1.0, "High": 1.1, "Critical": 1.25}
            mult = multipliers.get(app.business_criticality, 1.0)
            
        explanation_clauses = []
        for f in factors:
            if f.factor_type == "CVE":
                explanation_clauses.append("unresolved dependency vulnerabilities")
            elif f.factor_type == "License":
                explanation_clauses.append("license compliance conflicts")
            elif f.factor_type == "Maintenance":
                explanation_clauses.append("unmaintained/stale repositories")
            elif f.factor_type == "Architecture":
                explanation_clauses.append("direct vulnerabilities exposure")
                
        if explanation_clauses:
            clause_str = ", ".join(explanation_clauses[:-1])
            if len(explanation_clauses) > 1:
                clause_str += f", and {explanation_clauses[-1]}"
            else:
                clause_str = explanation_clauses[0]
            explanation = (
                f"The overall risk score is {float(risk_score.overall_score)} ({severity}). "
                f"This rating is driven by {clause_str}. Application business importance scaling is {mult}x."
            )
        else:
            explanation = (
                f"The overall risk score is {float(risk_score.overall_score)} ({severity}). "
                "No compliance violations, deprecated packages, or major CVE exposures are currently active."
            )
            
        return {
            "application_id": application_id,
            "overall_score": float(risk_score.overall_score),
            "severity": severity,
            "sub_scores": {
                "cvss_risk": float(risk_score.cvss_subscore),
                "license_risk": float(risk_score.license_subscore),
                "maintenance_risk": float(risk_score.maintenance_subscore),
                "architecture_risk": 40.0 if factors else 0.0
            },
            "business_multiplier": mult,
            "explanation": explanation,
            "factors": [{
                "type": f.factor_type,
                "impact": f.impact_level,
                "description": f.description
            } for f in factors]
        }
