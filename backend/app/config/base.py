import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Config:
    """Base configuration class."""
    APP_NAME = os.getenv("APP_NAME", "SBOM Analyzer")
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    
    # Database Settings
    DB_USER = os.getenv("DB_USER", "sbom_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "sbom_password")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "sbom_analyzer_db")
    
    # Fallback to connection string assembly
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRATION_HOURS", 24)))
    
    # File upload configurations
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), os.getenv("UPLOAD_FOLDER", "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", 25)) * 1024 * 1024
    
    # LLM Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo")
    
    # Logging Config
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")

class DevelopmentConfig(Config):
    """Development configuration overrides."""
    DEBUG = True
    ENV = "development"
    LOG_LEVEL = "DEBUG"

class TestingConfig(Config):
    """Testing configuration overrides."""
    TESTING = True
    DEBUG = True
    ENV = "testing"
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """Production configuration overrides."""
    DEBUG = False
    ENV = "production"
    # In production, require strict environment values
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    
    # Ensure logs path exists
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}
