from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("")
async def health_check():
    """
    Health check endpoint for AWS Lambda
    """
    return {"status": "healthy"} 