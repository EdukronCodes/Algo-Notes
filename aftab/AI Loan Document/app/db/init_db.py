from sqlalchemy import create_engine
from ..models.base import Base
from ..models.models import User, Document, LoanApplication, AuditLog
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

def init_db():
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 