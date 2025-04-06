from fastapi import FastAPI
from app.routers import health
from app.routers.v1 import library, document, chunk
from app.database.persistence import load_all_libraries, load_library_from_file
import logging
import os
import json
from uuid import UUID
from pathlib import Path
from contextlib import asynccontextmanager

# Configure logger
logger = logging.getLogger(__name__)

# Check for test data flag
TESTING_DATA = os.environ.get("TESTING_DATA", "false").lower() == "true"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the application
    # Load all libraries from disk
    libraries_loaded = load_all_libraries()
    logger.info(f"Loaded {libraries_loaded} libraries from disk on startup")
    
    # Load test data if testing mode is enabled
    if TESTING_DATA:
        logger.info("TESTING_DATA is set to true. Loading Andorra test library...")
        
        # Try multiple possible locations for the test file
        test_file_path = os.environ.get("TESTING_DATA_FILE")
        
        loaded = False
        if os.path.exists(test_file_path):
            try:
                if load_library_from_file(test_file_path):
                    logger.info(f"Successfully loaded test data from: {test_file_path}")
                    loaded = True
                else:
                    logger.warning(f"Failed to load test data from: {test_file_path}")
            except Exception as e:
                logger.warning(f"Error loading test data from {test_file_path}: {str(e)}")
        
        if not loaded:
            logger.error("Could not load test data from any location")
    
    yield  # Yield control back to FastAPI
    
    # Shutdown: Clean up resources if needed
    pass

app = FastAPI(
    title="Stack AI Vector DB",
    description="A FastAPI service for managing vector databases",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(health.router)
app.include_router(library.router, prefix="/api")
app.include_router(document.router, prefix="/api")
app.include_router(chunk.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 