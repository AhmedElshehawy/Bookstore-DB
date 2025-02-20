# Bookstore-DB

Bookstore-DB is tailored for managing the book database in the Bookstore Chatbot project. This repository is responsible for storing, upserting, and querying book data, and is designed to run in a serverless environment on AWS Lambda while interacting with an AWS RDS PostgreSQL instance.

You can try the chatbot [here](https://huggingface.co/spaces/elshehawy/BookBot)

## Table of Contents

- [Bookstore-DB](#bookstore-db)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Project Components](#project-components)
  - [Features](#features)
  - [Architecture](#architecture)
  - [Usage](#usage)
  - [API Endpoints](#api-endpoints)
  - [Environment Variables](#environment-variables)

## Overview

Bookstore-DB is one of four core repositories that power the Bookstore Chatbot ecosystem. It handles all database operations, ensuring that scraped book data is stored accurately and can be safely queried by other services.

## Project Components

This repository is part of a larger, multi-repo project:

- **[Bookstore Assistant](https://github.com/AhmedElshehawy/Bookstore_Assistant)**  
  Manages the chat interface, processes natural language queries, and interacts with the other parts of the system.

- **[Bookstore DB](https://github.com/AhmedElshehawy/Bookstore-DB)**  
  Responsible for storing and querying the book database.

- **[Bookstore Scraper](https://github.com/AhmedElshehawy/Bookstore_Scraper)**  
  Scrapes data from various web sources and feeds it into the database.

- **[Bookstore Frontend (BookBot)](https://huggingface.co/spaces/elshehawy/BookBot)**  
  Provides an interactive chat interface for users to engage with the bookstore chatbot.

## Features

- **Serverless Deployment**  
  Deployed on AWS Lambda to handle HTTP requests efficiently without server management.

- **Robust Database Operations**  
  Uses PostgreSQL on AWS RDS to store scraped book data while supporting both single and batch upsert operations.

- **Secure Query Execution**  
  Supports executing SQL queries via an endpoint that only permits `SELECT` statements, ensuring database safety.

## Architecture

The service is built using the FastAPI framework and leverages Mangum for AWS Lambda integration. Database interactions are securely managed via psycopg2, with strict safeguards to prevent non-SELECT queries. This design ensures that:

- **Scalability:** The AWS Lambda environment automatically scales with demand.
- **Security:** Only safe, read-only queries (SELECT) are permitted via the query endpoint.
- **Maintainability:** A modular code structure (models, routes, services) simplifies debugging and future enhancements.

## Usage

- **Upsert a Book**  
  Send a POST request to `/upsert` with a JSON payload representing a single book. Example:

  ```json
  {
      "title": "Example Book",
      "price": 19.99,
      "rating": 4,
      "description": "A book about examples.",
      "category": "Fiction",
      "upc": "123456789012",
      "num_available_units": 10,
      "image_url": "http://example.com/image.jpg",
      "book_url": "http://example.com/book"
  }
  ```

- **Batch Upsert Books**  
  Send a POST request to `/batch-upsert` with a JSON array containing multiple book objects.

- **Query Books**  
  Send a POST request to `/query` with a JSON payload that includes a SQL query. **Note:** Only `SELECT` queries are allowed for security.

- **Health Check**  
  Access the `/health` endpoint to ensure the service is running.

## API Endpoints

| Method | Endpoint         | Description                                        |
| ------ | ---------------- | -------------------------------------------------- |
| POST   | `/upsert`        | Upsert a single book into the database             |
| POST   | `/batch-upsert`  | Upsert multiple books in a single transaction      |
| POST   | `/query`         | Execute a `SELECT` query against the database      |
| GET    | `/health`        | Health check for the service                       |

## Environment Variables

Ensure to provide the following environment variables either via a `.env` file or your deployment environment:

- `DB_NAME` – Name of your PostgreSQL database
- `DB_USER` – Database user
- `DB_PASSWORD` – User's password for the database
- `DB_HOST` – Host address of the PostgreSQL database
- `DB_PORT` – Port number for the PostgreSQL database
- `TABLE_NAME` – Name of the table used to store book records

---

For further details on how these services interact within the Bookstore Chatbot ecosystem, please refer to the other repositories listed above.


