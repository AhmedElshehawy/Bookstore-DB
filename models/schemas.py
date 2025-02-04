from pydantic import BaseModel, Field
from typing import Optional
from .book_model import Book


class BookResponse(Book):
    """
    Book model for responses, including success message
    """
    message: Optional[str] = Field(None, description="Success or error message")

