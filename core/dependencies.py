from services import DatabaseHandler
import logging

logger = logging.getLogger(__name__)

async def get_db():
    """
    Get a database connection
    """
    db = DatabaseHandler()
    try:
        db.connect()
        yield db
    finally:
        db.close() 
