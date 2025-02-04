from fastapi import APIRouter, Depends, HTTPException
from core import get_db
from services import DatabaseHandler
from models import QueryRequest

query_router = APIRouter()

@query_router.post("/query")
async def query_books(query_request: QueryRequest, db: DatabaseHandler = Depends(get_db)):
    """
    Query the database for books
    """
    try:
        results = db.query_books(query_request.query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))