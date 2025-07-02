"""
Main FastAPI application for StockBook.

This module defines the FastAPI application with proper initialization,
middleware, and endpoints.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.persistence.database_initializer import initialize_database

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application lifecycle events.

    This function handles startup and shutdown events for the FastAPI app.

    Args:
        app: The FastAPI application instance

    Yields:
        None
    """
    # Startup
    try:
        # Get database path from environment or use default
        database_path = os.getenv("DATABASE_PATH", "/app/data/database/stockbook.db")

        # Initialize database on startup
        logger.info("Starting database initialization...")
        initialize_database(database_path)
        logger.info("Database initialization completed")

    except Exception as e:
        # Log error but don't crash the application
        # This allows the app to start even if DB init fails
        logger.error(f"Database initialization failed: {str(e)}")
        logger.warning("Application starting without database initialization")

    # Yield control to the application
    yield

    # Shutdown
    logger.info("Application shutting down")


# Create FastAPI app with lifespan management
app = FastAPI(
    title="StockBook API",
    version="1.0.0",
    description="Stock portfolio management and tracking API",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint providing API information.

    Returns:
        Dict containing API name, version, and available endpoints
    """
    return {
        "name": "StockBook API",
        "version": "1.0.0",
        "endpoints": {
            "/": "API information",
            "/health": "Health check endpoint",
            "/docs": "Interactive API documentation",
            "/redoc": "Alternative API documentation",
        },
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Dict indicating service health status
    """
    return {"status": "healthy", "service": "StockBook API"}
