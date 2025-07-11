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
from src.domain.exceptions import (
    AlreadyExistsError,
    BusinessRuleViolationError,
    DomainError,
    NotFoundError,
)
from src.infrastructure.persistence.database_initializer import initialize_database
from src.presentation.web.middleware.exception_handler import (
    already_exists_exception_handler,
    business_rule_violation_exception_handler,
    domain_exception_handler,
    generic_exception_handler,
    not_found_exception_handler,
)
from src.presentation.web.routers import stock_router
from src.version import __version__

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

    except (ValueError, TypeError, OSError, RuntimeError):
        # These are the exceptions that could be raised during database initialization:
        # - ValueError/TypeError from database_factory validation
        # - OSError from file system operations
        # - RuntimeError from SQLAlchemy configuration issues
        logger.exception("Database initialization failed")
        logger.warning("Application starting without database initialization")

    # Yield control to the application
    yield

    # Shutdown
    logger.info("Application shutting down")


# Create FastAPI app with lifespan management
app = FastAPI(
    title="StockBook API",
    version=__version__,
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

# Register exception handlers
app.add_exception_handler(NotFoundError, not_found_exception_handler)
app.add_exception_handler(AlreadyExistsError, already_exists_exception_handler)
app.add_exception_handler(
    BusinessRuleViolationError,
    business_rule_violation_exception_handler,
)
app.add_exception_handler(DomainError, domain_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

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
        "version": __version__,
        "endpoints": {
            "/": "API information",
            "/version": "Version information",
            "/health": "Health check endpoint",
            "/stocks": "Stock management endpoints",
            "/docs": "Interactive API documentation",
            "/redoc": "Alternative API documentation",
        },
    }


@app.get("/version")
async def version() -> dict[str, str]:
    """Version endpoint providing detailed version information.

    Returns:
        Dict containing version, release date, API version, and application name
    """
    from src.version import __api_version__, __release_date__

    return {
        "name": "StockBook",
        "version": __version__,
        "release_date": __release_date__,
        "api_version": __api_version__,
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dict indicating service health status
    """
    return {"status": "healthy", "service": "StockBook API"}
