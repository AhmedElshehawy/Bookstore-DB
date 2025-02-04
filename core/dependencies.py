from services import DatabaseHandler
from core.logger import setup_logger

logger = setup_logger("dependencies")

async def get_db():
    """
    Get a database connection
    """
    logger.debug("Creating new database connection")
    db = DatabaseHandler()
    try:
        db.connect()
        logger.debug("Database connection established")
        yield db
    finally:
        db.close()
        logger.debug("Database connection closed") 
