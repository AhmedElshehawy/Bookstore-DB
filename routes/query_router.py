from fastapi import APIRouter, Depends, HTTPException
from core.dependencies import get_db
from services import DatabaseHandler
from models import QueryRequest
from core.logger import setup_logger

logger = setup_logger("query_router")

query_router = APIRouter()

@query_router.post("/query")
async def query_books(query_request: QueryRequest, db: DatabaseHandler = Depends(get_db)):
    """
    Query the database for books
    """
    logger.info(f"Processing query request: {query_request.query}")
    try:
        results = db.query_books(query_request.query)
        result_count = len(results) if results else 0
        logger.info(f"Query completed successfully. Found {result_count} results")
        return {"results": results}
    except Exception as e:
        logger.error(f"Error processing query '{query_request.query}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))