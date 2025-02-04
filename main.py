from fastapi import FastAPI
from routes import query_router, upsert_router, health_router
import logging
from mangum import Mangum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Book Database API", description="API for managing books in a database")

# Include all routes
app.include_router(upsert_router, prefix="/upsert", tags=["upsert"])
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(query_router, prefix="/query", tags=["query"])

# Add Mangum handler for AWS Lambda
handler = Mangum(app)
