from fastapi import FastAPI
from routes import query_router, upsert_router, health_router
from core.logger import setup_logger
from mangum import Mangum

# Configure root logger
logger = setup_logger("bookstore_api")

app = FastAPI(title="Book Database API", description="API for managing books in a database")

# Include all routes
app.include_router(upsert_router, prefix="/upsert", tags=["upsert"])
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(query_router, prefix="/query", tags=["query"])

# Add Mangum handler for AWS Lambda
handler = Mangum(app)
