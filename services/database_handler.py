import json
import psycopg2
from psycopg2.extras import DictCursor
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime, timezone
from models import Book
from core.config import settings
from core.logger import setup_logger

# At the top of the class
logger = setup_logger("database")

class DatabaseHandler:
    """
    Handles all database operations for books, including connection management
    and CRUD operations with proper error handling.
    """
    def __init__(self):
        # Database connection parameters should be stored in environment variables
        self.db_params = {
            'dbname': settings.DB_NAME,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
            'host': settings.DB_HOST,
            'port': settings.DB_PORT
        }
        self.conn = None
        self.cur = None

    def connect(self):
        """Establishes database connection and creates a cursor."""
        try:
            self.conn = psycopg2.connect(**self.db_params)
            self.cur = self.conn.cursor(cursor_factory=DictCursor)
            logger.info("Successfully connected to database")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise Exception(f"Failed to connect to database: {str(e)}")

    def close(self):
        """Closes database connection and cursor safely."""
        if self.cur:
            logger.info("Closing cursor")
            self.cur.close()
        if self.conn:
            logger.info("Closing connection")
            self.conn.close()

    def get_book(self, upc: str) -> Optional[dict]:
        '''
        Get a book from the database.
        
        Args:
            upc: The UPC of the book to get
            
        Returns:
            dict: Book data if found, None otherwise
        '''
        try:
            logger.debug(f"Fetching book with UPC: {upc}")
            self.cur.execute(f"""
                SELECT title, price, rating, description, category, 
                       upc, num_available_units, image_url, book_url
                FROM {settings.TABLE_NAME} WHERE upc = %s
            """, (upc,))
            result = self.cur.fetchone()
            if result:
                logger.debug(f"Fetched book: {result}")
            else:
                logger.debug(f"No book found with UPC: {upc}")
            return dict(result) if result else None
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(f"Database error while fetching book with UPC {upc}: {str(e)}")
            raise Exception(f"Database error while fetching book with UPC {upc}: {str(e)}")

    def insert_book(self, book: Dict):
        """
        Inserts a new book into the database.
        
        Args:
            book: Book object containing the data to insert
        """
        try:
            logger.debug(f"Inserting book with URL: {book.get('book_url')}")
            self.cur.execute(f"""
                INSERT INTO {settings.TABLE_NAME} (
                    title, price, rating, description, category,
                    upc, num_available_units, image_url, book_url,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                book['title'], book['price'], book['rating'], book['description'],
                book['category'], book['upc'], book['num_available_units'],
                book['image_url'], book['book_url'],
                datetime.now(timezone.utc), datetime.now(timezone.utc)
            ))
            self.conn.commit()
            logger.info(f"Inserted new book with URL: {book.get('book_url')}")
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(f"Failed to insert book with URL {book.get('book_url')}: {str(e)}")
            raise Exception(f"Failed to insert book with URL {book.get('book_url')}: {str(e)}")

    def update_book(self, book: Dict):
        """
        Updates an existing book in the database.
        
        Args:
            book: Book object containing the updated data
        """
        try:
            logger.debug(f"Updating book with URL: {book.get('book_url')}")
            self.cur.execute(f"""
                UPDATE {settings.TABLE_NAME} SET
                    title = %s,
                    price = %s,
                    rating = %s,
                    description = %s,
                    category = %s,
                    num_available_units = %s,
                    image_url = %s,
                    book_url = %s,
                    updated_at = %s
                WHERE upc = %s
            """, (
                book['title'], book['price'], book['rating'], book['description'],
                book['category'], book['num_available_units'], book['image_url'],
                book['book_url'], datetime.now(timezone.utc), book['upc']
            ))
            self.conn.commit()
            logger.info(f"Updated book with URL: {book.get('book_url')}")
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(f"Failed to update book with URL {book.get('book_url')}: {str(e)}")
            raise Exception(f"Failed to update book with URL {book.get('book_url')}: {str(e)}")

    def books_are_different(self, existing_book: Dict, new_book: Dict) -> bool:
        """
        Compares an existing book with a new book to determine if they have different values.
        
        Args:
            existing_book: Dictionary containing current book data from database
            new_book: New Book object to compare against
            
        Returns:
            bool: True if books have different values, False if they're identical
        """
        difference_found = False
        for key in existing_book.keys():
            if existing_book[key] != new_book[key]:
                logger.info(f"{key}: {existing_book[key]} -> {new_book[key]}")
                difference_found = True
        
        return difference_found
        
    def process_book(self, book: Book):
        """
        Main method to process a book - handles the logic for inserting new books
        and updating existing ones only when there are changes.
        
        Args:
            book: Book object to process
        """
        book = json.loads(book.model_dump_json())
        book['price'] = float(book['price'])
        book['rating'] = int(book['rating'])
        book['num_available_units'] = int(book['num_available_units'])
        book['image_url'] = str(book['image_url'])
        book['book_url'] = str(book['book_url'])
        try:
            existing_book = self.get_book(book['upc'])
            
            existing_book['price'] = float(existing_book['price'])
            existing_book['rating'] = int(existing_book['rating'])
            existing_book['num_available_units'] = int(existing_book['num_available_units'])
            existing_book['image_url'] = str(existing_book['image_url'])
            existing_book['book_url'] = str(existing_book['book_url'])
            
            if not existing_book:
                # Book doesn't exist, insert it
                self.insert_book(book)
            elif self.books_are_different(existing_book, book):
                # Book exists but has different values, update it
                self.update_book(book)
            else:
                # Book exists and is identical, do nothing (skip)
                logger.info(f"Book {book['upc']} is identical to existing book, skipping update")
            
        except Exception as e:
            logger.error(f"Failed to process book {book['upc']}: {str(e)}")
            raise Exception(f"Failed to process book {book['upc']}: {str(e)}")
        
    def query_books(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """
        Query the database for books with proper error handling and parameter binding.
        Only allows SELECT queries for security.
        
        Args:
            query: The SQL query to execute with optional parameter placeholders (%s)
            params: Optional tuple of parameters to bind to the query
            
        Returns:
            List[Dict]: A list of book dictionaries where each dictionary contains book data
            
        Raises:
            ValueError: If the query is not a SELECT statement
            Exception: If there's an error executing the query
        """
        # Convert to uppercase for case-insensitive comparison
        normalized_query = query.strip().upper()
        
        # Check if query starts with SELECT
        if not normalized_query.startswith('SELECT'):
            logger.error("Attempted non-SELECT query execution blocked.")
            raise ValueError("Only SELECT queries are allowed for security reasons")
            
        try:
            logger.debug(f"Executing query: {query} with parameters: {params}")
            self.cur.execute(query, params)
            results = self.cur.fetchall()
            logger.debug(f"Query returned {len(results)} records")
            return [dict(row) for row in results]
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(f"Database error while querying books: {str(e)}")
            raise Exception(f"Database error while querying books: {str(e)}")
