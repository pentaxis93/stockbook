"""Main FastAPI application for StockBook.

This module defines the FastAPI application with proper initialization,
middleware, and endpoints.
"""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dependency_injection.composition_root import CompositionRoot
from src.infrastructure.persistence.database_initializer import initialize_database
from src.presentation.web.routers import stock_router

logger = logging.getLogger(__name__)

# DI container is stored in app.state instead of using global variable


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle events.

    This function handles startup and shutdown events for the FastAPI app.

    Args:
        fastapi_app: The FastAPI application instance

    Yields:
        None
    """
    # Access app state directly instead of using global

    # Startup
    try:
        # Get database path from environment or use default
        database_path = os.getenv("DATABASE_PATH", "/app/data/database/stockbook.db")

        # Initialize database on startup
        logger.info("Starting database initialization...")
        initialize_database(database_path)
        logger.info("Database initialization completed")

        # Configure dependency injection
        logger.info("Configuring dependency injection...")
        di_container = CompositionRoot.configure(database_path=database_path)

        # Store DI container in app state for access in dependencies
        fastapi_app.state.di_container = di_container
        logger.info("Dependency injection configured")

    except (ValueError, TypeError, OSError, RuntimeError) as e:
        # These are the exceptions that could be raised during database initialization:
        # - ValueError/TypeError from database_factory validation
        # - OSError from file system operations
        # - RuntimeError from SQLAlchemy configuration issues
        logger.error("Database initialization failed: %s", str(e))
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

# Include routers
app.include_router(stock_router.router)


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint providing API information.

    Returns:
        Dict containing API name, version, and available endpoints
    """
    return {
        "name": "StockBook API",
        "version": "1.0.0",
        "endpoints": {
            "/": "API information",
            "/health": "Health check endpoint",
            "/stocks": "Stock management endpoints",
            "/docs": "Interactive API documentation",
            "/redoc": "Alternative API documentation",
        },
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dict indicating service health status
    """
    return {"status": "healthy", "service": "StockBook API"}
