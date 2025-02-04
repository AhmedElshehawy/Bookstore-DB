from fastapi import APIRouter
from core.logger import setup_logger

logger = setup_logger("health_router")

health_router = APIRouter()

@health_router.get("/health")
async def health_check():
    """
    Health check endpoint for AWS Lambda
    """
    logger.debug("Health check requested")
    return {"status": "healthy"} 