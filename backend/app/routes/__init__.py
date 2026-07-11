# Routes package init
from app.routes.auth_routes import auth_bp
from app.routes.app_routes import app_bp
from app.routes.sbom_routes import sbom_bp
from app.routes.dependency_routes import dependency_bp
from app.routes.risk_routes import risk_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.report_routes import report_bp
from app.routes.copilot_routes import copilot_bp
from app.routes.vulnerability_routes import vulnerability_bp
from app.routes.license_routes import license_bp
from app.routes.maintenance_routes import maintenance_bp
from app.routes.attack_path_routes import attack_path_bp
from app.routes.notification_routes import notification_bp

def register_blueprints(app):
    """Register all routes blueprints to Flask application context."""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(app_bp, url_prefix='/api/applications')
    app.register_blueprint(sbom_bp, url_prefix='/api/sbom')
    app.register_blueprint(dependency_bp, url_prefix='/api/dependencies')
    app.register_blueprint(risk_bp, url_prefix='/api/risk')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(copilot_bp, url_prefix='/api/copilot')
    app.register_blueprint(vulnerability_bp, url_prefix='/api/vulnerabilities')
    app.register_blueprint(license_bp, url_prefix='/api/licenses')
    app.register_blueprint(maintenance_bp, url_prefix='/api/maintenance')
    app.register_blueprint(attack_path_bp, url_prefix='/api/attack-paths')
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
