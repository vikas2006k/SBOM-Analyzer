import os
import pytest
from app.services.parser_service import ParserService
from app.services.dependency_service import DependencyService
from app.models.application import Application
from app.models.sbom_upload import SBOMUpload
from app.models.library import Library
from app.models.dependency import Dependency
from app.database.connection import db

MOCK_DIR = os.path.join(os.path.dirname(__file__), 'mock_data')

def test_parse_cyclonedx():
    """Verify parsing CycloneDX JSON SBOM structure."""
    file_path = os.path.join(MOCK_DIR, 'cyclonedx_sample.json')
    result = ParserService.parse_sbom_file(file_path, 'json')
    
    assert result["application_name"] == "PaymentGateway"
    assert result["application_version"] == "1.0.0"
    assert len(result["libraries"]) == 3
    assert len(result["dependencies"]) == 3
    
    # Check library parsing details
    libs = {lib["name"]: lib for lib in result["libraries"]}
    assert "spring-boot-starter-web" in libs
    assert libs["spring-boot-starter-web"]["version"] == "3.1.2"
    assert libs["spring-boot-starter-web"]["ecosystem"] == "npm"
    assert libs["spring-boot-starter-web"]["license_name"] == "Apache-2.0"

def test_parse_spdx():
    """Verify parsing SPDX JSON SBOM structure."""
    file_path = os.path.join(MOCK_DIR, 'spdx_sample.json')
    result = ParserService.parse_sbom_file(file_path, 'json')
    
    assert result["application_name"] == "AuthService"
    assert result["application_version"] == "1.2.0"
    assert len(result["libraries"]) == 2
    assert len(result["dependencies"]) == 2
    
    libs = {lib["name"]: lib for lib in result["libraries"]}
    assert "jsonwebtoken" in libs
    assert libs["jsonwebtoken"]["version"] == "9.0.0"
    assert libs["jsonwebtoken"]["license_name"] == "MIT"

def test_parse_csv():
    """Verify parsing tabular CSV dependencies SBOM."""
    file_path = os.path.join(MOCK_DIR, 'dependencies_sample.csv')
    result = ParserService.parse_sbom_file(file_path, 'csv', 'PaymentAPI', '2.0.0')
    
    assert result["application_name"] == "PaymentAPI"
    assert result["application_version"] == "2.0.0"
    assert len(result["libraries"]) == 4
    assert len(result["dependencies"]) == 4
    
    libs = {lib["name"]: lib for lib in result["libraries"]}
    assert "requests" in libs
    assert libs["requests"]["version"] == "2.31.0"
    assert libs["requests"]["ecosystem"] == "pypi"
    assert libs["requests"]["license_name"] == "Apache-2.0"

def test_validate_sbom_valid():
    """Ensure standard valid parsed SBOM validates correctly."""
    parsed_data = {
        "application_name": "TestApp",
        "application_version": "1.0.0",
        "libraries": [
            {"name": "lib-a", "version": "1.0.0", "license_name": "MIT"},
            {"name": "lib-b", "version": "2.0.1", "license_name": "Apache-2.0"}
        ],
        "dependencies": [
            {"parent_name": "TestApp", "parent_version": "1.0.0", "child_name": "lib-a", "child_version": "1.0.0"},
            {"parent_name": "lib-a", "parent_version": "1.0.0", "child_name": "lib-b", "child_version": "2.0.1"}
        ]
    }
    report = ParserService.validate_sbom(parsed_data)
    assert report["valid"] is True
    assert len(report["errors"]) == 0

def test_validate_sbom_circular():
    """Verify circular references are detected and report errors."""
    parsed_data = {
        "application_name": "CycleApp",
        "application_version": "1.0.0",
        "libraries": [
            {"name": "lib-x", "version": "1.0.0"},
            {"name": "lib-y", "version": "1.0.0"}
        ],
        "dependencies": [
            {"parent_name": "lib-x", "parent_version": "1.0.0", "child_name": "lib-y", "child_version": "1.0.0"},
            {"parent_name": "lib-y", "parent_version": "1.0.0", "child_name": "lib-x", "child_version": "1.0.0"}
        ]
    }
    report = ParserService.validate_sbom(parsed_data)
    assert report["valid"] is False
    assert any("Circular dependency" in err for err in report["errors"])

def test_dependency_graph_resolutions(app):
    """Verify NetworkX DiGraph creation and depth resolution algorithms integration."""
    with app.app_context():
        # Setup application profile
        app_model = Application(name="WebPortal", version="2.1.0", business_criticality="High")
        db.session.add(app_model)
        db.session.commit()
        
        # Setup libraries
        lib1 = Library(name="express", version="4.18.2", ecosystem="npm", license_name="MIT")
        lib2 = Library(name="debug", version="4.3.4", ecosystem="npm", license_name="MIT")
        db.session.add_all([lib1, lib2])
        db.session.commit()
        
        # Setup edges
        dep1 = Dependency(application_id=app_model.id, parent_library_id=None, child_library_id=lib1.id, depth=1)
        dep2 = Dependency(application_id=app_model.id, parent_library_id=lib1.id, child_library_id=lib2.id, depth=1)
        db.session.add_all([dep1, dep2])
        db.session.commit()
        
        dep_service = DependencyService()
        
        # Verify cycles
        cycle_report = dep_service.detect_cycles(app_model.id)
        assert cycle_report["has_cycles"] is False
        
        # Resolve depths
        status = dep_service.resolve_transitive_depths(app_model.id)
        assert status is True
        
        # Check resolved details
        resolved_dep2 = Dependency.query.filter_by(child_library_id=lib2.id).first()
        assert resolved_dep2.depth == 2
        assert resolved_dep2.is_transitive is True
        
        # React Flow JSON adjacency formatting check
        flow_graph = dep_service.get_adjacency_matrix(app_model.id)
        assert len(flow_graph["nodes"]) == 3
        assert len(flow_graph["edges"]) == 2
        assert flow_graph["metrics"]["max_depth"] == 2
