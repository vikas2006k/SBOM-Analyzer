import os
import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.database.connection import db
from app.models.application import Application
from app.models.report import AnalysisReport
from app.services.risk_service import RiskService
from app.services.vulnerability_service import VulnerabilityService
from app.services.license_service import LicenseService
from app.services.maintenance_service import MaintenanceService
from app.utils.logger import Logger

logger = Logger.get_logger('app')

class ReportService:
    """Service implementing professional PDF compilation and CSV manifest exports."""

    def __init__(self):
        self.risk_service = RiskService()
        self.vuln_service = VulnerabilityService()
        self.license_service = LicenseService()
        self.maint_service = MaintenanceService()

    def generate_executive_pdf(self, application_id, user_id):
        """Build professional PDF document summarizing security, licensing, and compliance health."""
        logger.info(f"Generating Executive PDF Report for application {application_id}")
        
        app = db.session.get(Application, application_id)
        if not app:
            raise ValueError(f"Application with ID {application_id} not found")
            
        risk = self.risk_service.get_latest_risk_score(application_id)
        vulns = self.vuln_service.get_vulnerabilities_by_application(application_id)
        licenses = self.license_service.audit_licenses(application_id)
        maint = self.maint_service.check_maintenance_health(application_id)
        
        # 1. Prepare directory and file path
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
        os.makedirs(output_dir, exist_ok=True)
        filename = f"SentinelSBOM_Executive_{application_id}_{int(datetime.now().timestamp())}.pdf"
        file_path = os.path.join(output_dir, filename)
        
        doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=colors.HexColor('#4f46e5'), # Indigo
            spaceAfter=15
        )
        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#64748b'), # Slate grey
            spaceAfter=30
        )
        h2_style = ParagraphStyle(
            'H2Style',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=15,
            spaceAfter=10
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#334155'),
            leading=14,
            spaceAfter=8
        )
        
        # Cover Headers
        story.append(Paragraph("SentinelSBOM Security Report", title_style))
        story.append(Paragraph(f"Application: {app.name} v{app.version} | Target Environment Business Criticality: {app.business_criticality}", subtitle_style))
        story.append(Spacer(1, 10))
        
        # Risk Metrics Table Block
        risk_color = '#ef4444' if risk['overall_score'] >= 75.0 else ('#f97316' if risk['overall_score'] >= 50.0 else '#eab308')
        summary_data = [
            [Paragraph("<b>Metric Dimension</b>", body_style), Paragraph("<b>Score Status</b>", body_style), Paragraph("<b>Criticality Level</b>", body_style)],
            [Paragraph("Composite Risk Score", body_style), Paragraph(str(risk['overall_score']), body_style), Paragraph(f"<font color='{risk_color}'><b>{risk['severity']}</b></font>", body_style)],
            [Paragraph("Vulnerabilities (CVEs)", body_style), Paragraph(str(len(vulns)), body_style), Paragraph(f"{sum(1 for v in vulns if v['severity']=='Critical')} Critical, {sum(1 for v in vulns if v['severity']=='High')} High", body_style)],
            [Paragraph("License Compliance Score", body_style), Paragraph(str(licenses['license_score']), body_style), Paragraph(f"{licenses['conflicts_count']} Conflicts", body_style)],
            [Paragraph("Maintenance Score Index", body_style), Paragraph(str(maint['average_maintenance_score']), body_style), Paragraph(f"{maint['deprecated_count']} Deprecated Packages", body_style)]
        ]
        
        t = Table(summary_data, colWidths=[200, 150, 180])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        
        story.append(Paragraph("Executive Supply Chain Risk Metrics Summary", h2_style))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # Explanation text
        story.append(Paragraph("<b>AI Security Analysis Overview:</b>", body_style))
        story.append(Paragraph(risk["explanation"], body_style))
        story.append(Spacer(1, 15))
        
        # Vulnerabilities Catalog
        story.append(Paragraph("Vulnerabilities Catalog (Top 5 CVEs)", h2_style))
        if vulns:
            vuln_headers = [[Paragraph("<b>CVE ID</b>", body_style), Paragraph("<b>Library</b>", body_style), Paragraph("<b>CVSS Score</b>", body_style), Paragraph("<b>Severity</b>", body_style), Paragraph("<b>Patch Version</b>", body_style)]]
            for v in vulns[:5]:
                vuln_headers.append([
                    Paragraph(v["cve_id"], body_style),
                    Paragraph(v["affected_library"], body_style),
                    Paragraph(str(v["cvss_score"]), body_style),
                    Paragraph(f"<b>{v['severity']}</b>", body_style),
                    Paragraph(v["patched_version"] or "No patch", body_style)
                ])
            vt = Table(vuln_headers, colWidths=[110, 140, 80, 100, 100])
            vt.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6)
            ]))
            story.append(vt)
        else:
            story.append(Paragraph("No active CVE vulnerability warnings detected in code packages.", body_style))
            
        story.append(Spacer(1, 15))
        
        # License compliance conflicts
        story.append(Paragraph("License Compliance & Incompatibilities", h2_style))
        if licenses["conflicts"]:
            lic_headers = [[Paragraph("<b>Vulnerable Library</b>", body_style), Paragraph("<b>License</b>", body_style), Paragraph("<b>Category</b>", body_style), Paragraph("<b>Description</b>", body_style)]]
            for c in licenses["conflicts"][:5]:
                lic_headers.append([
                    Paragraph(c["library_name"], body_style),
                    Paragraph(c["license_name"], body_style),
                    Paragraph(c["category"], body_style),
                    Paragraph(c["description"], body_style)
                ])
            lt = Table(lic_headers, colWidths=[110, 100, 100, 220])
            lt.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6)
            ]))
            story.append(lt)
        else:
            story.append(Paragraph("No license conflicts or viral copyleft constraints were identified.", body_style))
            
        story.append(Spacer(1, 15))
        
        # Strategic Advice
        story.append(Paragraph("Remediation Recommendations Checklist", h2_style))
        recs = licenses.get("recommendations", [])
        if vulns:
            recs.insert(0, f"Upgrade top vulnerable packages ({', '.join([v['affected_library'] for v in vulns[:3]])}) to patch active RCE threat vectors.")
        
        if recs:
            for idx, rec in enumerate(recs[:4]):
                story.append(Paragraph(f"<b>[ ] Action {idx+1}:</b> {rec}", body_style))
        else:
            story.append(Paragraph("Codebase is fully optimized. Schedule next scanning cycle.", body_style))
            
        # Build doc
        doc.build(story)
        
        # Write record in AnalysisReport table
        report_record = AnalysisReport(
            application_id=application_id,
            report_type="Executive",
            format="PDF",
            file_path=file_path,
            generated_by=user_id
        )
        db.session.add(report_record)
        db.session.commit()
        
        # Return web accessible or local path details
        return {
            "report_id": report_record.id,
            "filename": filename,
            "absolute_path": file_path,
            "status": "success"
        }

    def generate_developer_csv(self, application_id, user_id):
        """Export flat CSV containing libraries patching sequences."""
        logger.info(f"Generating Developer CSV Report for application {application_id}")
        
        app = db.session.get(Application, application_id)
        if not app:
            raise ValueError(f"Application with ID {application_id} not found")
            
        # Get libraries and vulnerabilities matching
        vulns = self.vuln_service.get_vulnerabilities_by_application(application_id)
        maint = self.maint_service.check_maintenance_health(application_id)
        
        # Map libs status
        libs_maint = {d["library_name"]: d for d in maint["dependencies"]}
        
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
        os.makedirs(output_dir, exist_ok=True)
        filename = f"SentinelSBOM_DeveloperPatch_{application_id}_{int(datetime.now().timestamp())}.csv"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Library Name", "Current Version", "CVE ID", "CVSS Score", 
                "Severity", "Patched Version", "Patch Available", 
                "License Name", "Maintenance Score", "Bus Factor", "Deprecation Status", "Remediation Action"
            ])
            
            # Map vulnerability columns
            seen_libs = set()
            for v in vulns:
                lib_name = v["affected_library"]
                lib_ver = v["affected_version"]
                seen_libs.add((lib_name, lib_ver))
                
                m_info = libs_maint.get(lib_name, {"bus_factor": 1, "is_deprecated": False, "maintenance_score": 100})
                
                action = f"Upgrade package to version {v['patched_version']}." if v["patched_version"] else "Restrict exposure or seek alternatives."
                writer.writerow([
                    lib_name, lib_ver, v["cve_id"], v["cvss_score"],
                    v["severity"], v["patched_version"] or "N/A", v["patch_available"],
                    v.get("license", "Unknown"), m_info["maintenance_score"],
                    m_info["bus_factor"], m_info["is_deprecated"], action
                ])
                
            # Document non-vulnerable libraries that are deprecated or have low maintenance
            for d in maint["dependencies"]:
                lib_key = (d["library_name"], d["library_version"])
                if lib_key not in seen_libs:
                    if d["is_deprecated"] or d["maintenance_score"] < 50.0:
                        action = "Replace deprecated library." if d["is_deprecated"] else "Review alternative active libraries."
                        writer.writerow([
                            d["library_name"], d["library_version"], "N/A", 0.0,
                            "Clean", "N/A", "N/A",
                            d["license"], d["maintenance_score"],
                            d["bus_factor"], d["is_deprecated"], action
                        ])
                        
        report_record = AnalysisReport(
            application_id=application_id,
            report_type="Developer",
            format="CSV",
            file_path=file_path,
            generated_by=user_id
        )
        db.session.add(report_record)
        db.session.commit()
        
        return {
            "report_id": report_record.id,
            "filename": filename,
            "absolute_path": file_path,
            "status": "success"
        }
