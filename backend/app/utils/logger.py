import os
import logging
from logging.handlers import RotatingFileHandler

class Logger:
    """Central logging configuration class supporting multiple rotating logs."""
    _initialized = False

    @classmethod
    def setup_logging(cls, log_dir, log_level_str="INFO"):
        """Initialize all standard rotating log files handler connections."""
        if cls._initialized:
            return
        
        os.makedirs(log_dir, exist_ok=True)
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)
        
        # Standard formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s'
        )

        # 1. Main App Logger setup
        app_handler = RotatingFileHandler(os.path.join(log_dir, 'app.log'), maxBytes=10*1024*1024, backupCount=5)
        app_handler.setFormatter(formatter)
        app_logger = logging.getLogger('app')
        app_logger.setLevel(log_level)
        app_logger.addHandler(app_handler)

        # 2. Security Logger setup
        security_handler = RotatingFileHandler(os.path.join(log_dir, 'security.log'), maxBytes=10*1024*1024, backupCount=5)
        security_handler.setFormatter(formatter)
        security_logger = logging.getLogger('security')
        security_logger.setLevel(log_level)
        security_logger.addHandler(security_handler)

        # 3. Error Logger setup
        error_handler = RotatingFileHandler(os.path.join(log_dir, 'error.log'), maxBytes=10*1024*1024, backupCount=5)
        error_handler.setFormatter(formatter)
        error_logger = logging.getLogger('error')
        error_logger.setLevel(logging.ERROR)
        error_logger.addHandler(error_handler)

        # 4. AI Copilot Logger setup
        ai_handler = RotatingFileHandler(os.path.join(log_dir, 'ai.log'), maxBytes=10*1024*1024, backupCount=5)
        ai_handler.setFormatter(formatter)
        ai_logger = logging.getLogger('ai')
        ai_logger.setLevel(log_level)
        ai_logger.addHandler(ai_handler)

        cls._initialized = True

    @staticmethod
    def get_logger(name='app'):
        """Retrieve target logger by name."""
        return logging.getLogger(name)
