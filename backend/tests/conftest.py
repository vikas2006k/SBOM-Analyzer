import os
import pytest
from app import create_app
from app.database.connection import db
from app.models.role import Role
from app.models.user import User

@pytest.fixture(scope='session')
def app():
    """Create and configure a new Flask app instance for testing."""
    os.environ["APP_ENV"] = "testing"
    # Force testing configuration
    app = create_app("testing")
    
    with app.app_context():
        # Recreate tables in memory
        db.create_all()
        
        # Seed default test role and admin user
        role = Role(name="admin", permissions="[]")
        db.session.add(role)
        db.session.commit()
        
        user = User(
            username="test_admin",
            email="test_admin@enterprise.com",
            password_hash="pbkdf2:sha256:mock_hash", # mock hash
            role_id=role.id
        )
        db.session.add(user)
        db.session.commit()
        
        yield app
        
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the application."""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Creates a new database session for a test."""
    with app.app_context():
        yield db.session
        db.session.rollback()
