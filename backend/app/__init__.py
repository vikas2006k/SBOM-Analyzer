from flask import Flask
from flask_cors import CORS
from app.config.base import config_by_name
from app.database.connection import init_db
from app.routes import register_blueprints
from app.middlewares.error_middleware import register_error_handlers
from app.utils.logger import Logger

def create_app(config_name="development"):
    """Flask Application Factory creating context environments."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_by_name[config_name])
    
    # Setup CORS rules
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Setup logging configuration
    Logger.setup_logging(app.config["LOG_DIR"], app.config["LOG_LEVEL"])
    app.logger = Logger.get_logger("app")
    app.logger.info("Application logging configured successfully.")
    
    # Initialize Database & Migrations
    init_db(app)
    app.logger.info("Database extensions registered.")
    
    # Register API blueprints
    register_blueprints(app)
    app.logger.info("Routes blueprints bound.")
    
    # Register global exceptions middleware handlers
    register_error_handlers(app)
    app.logger.info("Exceptions handlers bound.")
    
    return app
