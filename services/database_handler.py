import json
import psycopg2
from psycopg2.extras import DictCursor, execute_values, execute_batch
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

    def insert_book(self, book: Dict, commit: bool = True):
        """
        Inserts a new book into the database.
        
        Args:
            book: Book data to insert.
            commit: If True, commits the transaction immediately.
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
            if commit:
                self.conn.commit()
            logger.info(f"Inserted new book with URL: {book.get('book_url')}")
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(f"Failed to insert book with URL {book.get('book_url')}: {str(e)}")
            raise Exception(f"Failed to insert book with URL {book.get('book_url')}: {str(e)}")

    def update_book(self, book: Dict, commit: bool = True):
        """
        Updates an existing book in the database.
        
        Args:
            book: Book data to update.
            commit: If True, commits the transaction immediately.
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
            if commit:
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
        Processes a single book by delegating to the bulk processing method.
        This ensures consistent handling whether a single or multiple books are processed.
        """
        self.process_books_batch([book])

    def process_books_batch(self, books: List[Book]):
        """
        Processes a list of books in a single transaction using bulk operations.
        This version fetches all existing records in one query and then performs bulk 
        inserts and bulk updates using execute_values and execute_batch.
        
        Args:
            books: List[Book] objects to process.
        """
        if not books:
            logger.info("No books provided for batch processing.")
            return

        try:
            # Prepare list of book data dictionaries and corresponding UPCs.
            book_data_list = []
            upcs = []
            for book in books:
                book_data = json.loads(book.model_dump_json())
                # Normalize data types.
                book_data['price'] = float(book_data['price'])
                book_data['rating'] = int(book_data['rating'])
                book_data['num_available_units'] = int(book_data['num_available_units'])
                book_data['image_url'] = str(book_data['image_url'])
                book_data['book_url'] = str(book_data['book_url'])
                book_data_list.append(book_data)
                upcs.append(book_data['upc'])
            
            # Bulk fetch of existing books.
            select_query = f"""
                SELECT title, price, rating, description, category, 
                       upc, num_available_units, image_url, book_url
                FROM {settings.TABLE_NAME} 
                WHERE upc IN %s
            """
            self.cur.execute(select_query, (tuple(upcs),))
            results = self.cur.fetchall()
            
            existing_books = {}
            if results:
                for row in results:
                    book_record = dict(row)
                    # Normalize type conversion for proper comparison.
                    book_record['price'] = float(book_record['price'])
                    book_record['rating'] = int(book_record['rating'])
                    book_record['num_available_units'] = int(book_record['num_available_units'])
                    book_record['image_url'] = str(book_record['image_url'])
                    book_record['book_url'] = str(book_record['book_url'])
                    existing_books[book_record['upc']] = book_record
            
            # Prepare bulk insert and update data.
            inserts = []
            updates = []
            current_time = datetime.now(timezone.utc)
            for book_data in book_data_list:
                upc = book_data['upc']
                if upc not in existing_books:
                    # New book: prepare tuple for bulk insert.
                    inserts.append((
                        book_data['title'], book_data['price'], book_data['rating'], book_data['description'],
                        book_data['category'], book_data['upc'], book_data['num_available_units'],
                        book_data['image_url'], book_data['book_url'], current_time, current_time
                    ))
                elif self.books_are_different(existing_books[upc], book_data):
                    # Updated book: prepare tuple for bulk update.
                    updates.append((
                        book_data['title'], book_data['price'], book_data['rating'], book_data['description'],
                        book_data['category'], book_data['num_available_units'], book_data['image_url'],
                        book_data['book_url'], current_time, book_data['upc']
                    ))
                else:
                    logger.info(f"No changes for book with UPC: {upc}, skipping.")

            # Bulk insert using execute_values if there are records to insert.
            if inserts:
                insert_query = f"""
                    INSERT INTO {settings.TABLE_NAME} (
                        title, price, rating, description, category,
                        upc, num_available_units, image_url, book_url,
                        created_at, updated_at
                    ) VALUES %s
                """
                execute_values(self.cur, insert_query, inserts)
                logger.info(f"Bulk-inserted {len(inserts)} new books.")
            
            # Bulk update using execute_batch if there are records to update.
            if updates:
                update_query = f"""
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
                """
                execute_batch(self.cur, update_query, updates)
                logger.info(f"Bulk-updated {len(updates)} books.")

            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(f"Batch processing failed: {str(e)}")
            raise Exception(f"Batch processing failed: {str(e)}")

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
