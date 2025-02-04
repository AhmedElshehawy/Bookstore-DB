from fastapi import APIRouter, HTTPException, Depends
from models import Book, BookResponse
from core.dependencies import get_db
from services import DatabaseHandler
from core.logger import setup_logger
import logging
import psycopg2

logger = setup_logger("upsert_router")

upsert_router = APIRouter()

@upsert_router.post("/upsert", response_model=BookResponse)
async def upsert_book(book: Book, db: DatabaseHandler = Depends(get_db)):
    """
    Upsert a book into the database
    """
    try:
        db.process_book(book)
        return BookResponse(**book.model_dump(), message="Book processed successfully")
    except psycopg2.Error as e:
        logger.error(f"Database error while processing book: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
