from fastapi import APIRouter, HTTPException, Depends
from models import Book, BookResponse
from core.dependencies import get_db
from services import DatabaseHandler
from core.logger import setup_logger
import psycopg2

logger = setup_logger("upsert_router")

upsert_router = APIRouter()

@upsert_router.post("/upsert", response_model=BookResponse)
async def upsert_book(book: dict, db: DatabaseHandler = Depends(get_db)):
    """
    Upsert a book into the database
    """
    book_model = Book(**book)
    logger.info(f"Processing upsert request for book: {book_model.title} (UPC: {book_model.upc})")
    try:
        db.process_book(book_model)
        logger.info(f"Successfully processed book: {book_model.title} (UPC: {book_model.upc})")
        return BookResponse(**book, message="Book processed successfully")
    except psycopg2.Error as e:
        logger.error(f"Database error while processing book '{book_model.title}': {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except ValueError as e:
        logger.error(f"Validation error for book '{book_model.title}': {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing book '{book_model.title}': {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
