from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import declarative_base

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database connection with Flask app context."""
    db.init_app(app)
    migrate.init_app(app, db)

def db_session():
    """Context-aware db session generator."""
    return db.session
