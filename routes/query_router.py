from fastapi import APIRouter, Depends, HTTPException
from routes.upsert_router import get_db
from services import DatabaseHandler

query_router = APIRouter()

@query_router.get("/query")
async def query_books(query: str, db: DatabaseHandler = Depends(get_db)):
    """
    Query the database for books
    """
    try:
        results = db.query_books(query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))