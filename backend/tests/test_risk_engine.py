import pytest
from app.models.application import Application
from app.models.library import Library
from app.models.dependency import Dependency
from app.models.vulnerability import Vulnerability
from app.database.connection import db
from app.services.vulnerability_service import VulnerabilityService
from app.services.license_service import LicenseService
from app.services.maintenance_service import MaintenanceService
from app.services.risk_service import RiskService
from app.services.attack_path_service import AttackPathService

def test_vulnerability_severity_classification():
    """Verify CVSS score mapping to correct severity labels."""
    assert VulnerabilityService.classify_severity(10.0) == "Critical"
    assert VulnerabilityService.classify_severity(9.8) == "Critical"
    assert VulnerabilityService.classify_severity(8.5) == "High"
    assert VulnerabilityService.classify_severity(7.0) == "High"
    assert VulnerabilityService.classify_severity(6.5) == "Medium"
    assert VulnerabilityService.classify_severity(4.0) == "Medium"
    assert VulnerabilityService.classify_severity(3.5) == "Low"
    assert VulnerabilityService.classify_severity(0.0) == "Informational"

def test_license_category_detection(app):
    """Verify spelling classifications map to proper license categories."""
    with app.app_context():
        service = LicenseService()
        assert service.detect_category("MIT") == "Permissive"
        assert service.detect_category("Apache 2.0") == "Permissive"
        assert service.detect_category("BSD-3-Clause") == "Permissive"
        assert service.detect_category("GPL-3.0") == "Copyleft"
        assert service.detect_category("LGPL-3.0") == "Weak-Copyleft"
        assert service.detect_category("MPL-2.0") == "Weak-Copyleft"
        assert service.detect_category("Unknown-Lic") == "Unknown"

def test_maintenance_scoring(app):
    """Verify project health calculations from maintenance logs."""
    with app.app_context():
        service = MaintenanceService()
        lib = Library(name="test-maint", version="1.0.0", ecosystem="npm")
        db.session.add(lib)
        db.session.commit()
        
        # Low risk record
        record = service.get_or_create_record(lib)
        record.bus_factor = 5
        record.commit_frequency_annual = 150
        record.is_deprecated = False
        db.session.commit()
        
        analysis = service.calculate_score(record)
        assert analysis["score"] >= 80.0
        assert analysis["health_level"] == "Healthy"
        
        # High risk deprecated record
        record.is_deprecated = True
        record.bus_factor = 1
        db.session.commit()
        
        analysis = service.calculate_score(record)
        assert analysis["score"] < 50.0
        assert analysis["health_level"] == "Critical Risk"
        assert any("deprecated" in w for w in analysis["warnings"])

def test_composite_risk_calculations(app):
    """Verify the risk aggregations weights and explanations generation."""
    with app.app_context():
        # 1. Setup mock application details
        test_app = Application(name="PortalRiskApp", version="1.0.0", business_criticality="High")
        db.session.add(test_app)
        db.session.commit()
        
        # 2. Setup library and vulnerabilities
        lib = Library(name="jsonwebtoken", version="9.0.0", ecosystem="npm", license_name="MIT")
        db.session.add(lib)
        db.session.commit()
        
        # CVE 9.8 Critical
        vuln = Vulnerability(
            cve_id="CVE-2023-51074",
            cvss_score=9.8,
            severity="Critical",
            description="Signature validation bypass threat",
            patched_version="9.0.1"
        )
        db.session.add(vuln)
        db.session.commit()
        
        # Link dependency edge
        edge = Dependency(application_id=test_app.id, parent_library_id=None, child_library_id=lib.id, depth=1)
        db.session.add(edge)
        db.session.commit()
        
        # 3. Match vulnerabilities & compute score
        vuln_service = VulnerabilityService()
        vuln_service.match_vulnerabilities_for_application(test_app.id)
        
        risk_service = RiskService()
        report = risk_service.calculate_risk_score(test_app.id)
        
        assert report["overall_score"] > 50.0
        assert report["severity"] in ["High", "Critical"]
        assert "max CVSS vulnerability score of 9.8" in report["explanation"]
        assert len(report["factors"]) > 0

def test_attack_path_traversal(app):
    """Verify NetworkX paths traversing algorithms."""
    with app.app_context():
        # Setup app
        test_app = Application(name="NetworkXApp", version="1.0.0", business_criticality="Medium")
        db.session.add(test_app)
        db.session.commit()
        
        # Setup transitive nodes
        lib_direct = Library(name="requests", version="2.30.0", ecosystem="pypi", license_name="Apache-2.0")
        lib_transitive = Library(name="urllib3", version="2.0.0", ecosystem="pypi", license_name="MIT")
        db.session.add_all([lib_direct, lib_transitive])
        db.session.commit()
        
        # Setup edges: App -> Direct -> Transitive
        edge1 = Dependency(application_id=test_app.id, parent_library_id=None, child_library_id=lib_direct.id, depth=1)
        edge2 = Dependency(application_id=test_app.id, parent_library_id=lib_direct.id, child_library_id=lib_transitive.id, depth=2)
        db.session.add_all([edge1, edge2])
        db.session.commit()
        
        # Setup Vulnerability on Transitive
        vuln = Vulnerability(
            cve_id="CVE-2023-43804",
            cvss_score=5.3,
            severity="Medium",
            description="Cookie leakage redirect vulnerability",
            patched_version="2.0.7"
        )
        db.session.add(vuln)
        db.session.commit()
        
        # Match vulns
        vuln_service = VulnerabilityService()
        vuln_service.match_vulnerabilities_for_application(test_app.id)
        
        # Run Attack Path analysis
        ap_service = AttackPathService()
        report = ap_service.analyze_attack_paths(test_app.id)
        
        assert report["attack_paths_count"] == 1
        assert len(report["root_cause_analysis"]) == 1
        assert report["root_cause_analysis"][0]["direct_dependency"] == "requests@2.30.0"
        
        # Visual graph checking
        graph = report["graph_visualization"]
        assert len(graph["nodes"]) == 3 # App, Direct, Transitive
        assert len(graph["edges"]) == 2
        # Check node color attributes
        nodes_dict = {n["id"]: n for n in graph["nodes"]}
        assert nodes_dict["urllib3@2.0.0"]["data"]["status"] == "vulnerable"
