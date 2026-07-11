from sqlalchemy import text
from app.database.connection import db

class DbConnector:
    """Wrapper class executing raw SQL commands directly inside db context."""
    
    @staticmethod
    def execute_raw_sql(query_str, params=None):
        """Execute raw SELECT SQL query statements."""
        params = params or {}
        session = db.session
        result = session.execute(text(query_str), params)
        return result

    @staticmethod
    def execute_raw_write(query_str, params=None, commit=True):
        """Execute raw INSERT/UPDATE/DELETE queries."""
        params = params or {}
        session = db.session
        result = session.execute(text(query_str), params)
        if commit:
            session.commit()
        return result
