"""
Main FastAPI application for StockBook.

This module defines the FastAPI application with proper initialization,
middleware, and endpoints.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dependency_injection.composition_root import CompositionRoot
from dependency_injection.di_container import DIContainer
from src.application.services.stock_application_service import StockApplicationService
from src.infrastructure.persistence.database_initializer import initialize_database
from src.presentation.web.routers import stock_router

logger = logging.getLogger(__name__)

# Global DI container
_di_container: Optional[DIContainer] = None
"""Global dependency injection container instance."""


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
    global _di_container

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
        _di_container = CompositionRoot.configure(database_path=database_path)

        # Set up service factory for stock router
        def stock_service_factory() -> StockApplicationService:
            """
            Factory function to create StockApplicationService instances.

            Returns:
                StockApplicationService: The stock application service instance

            Raises:
                RuntimeError: If DI container is not initialized
            """
            if _di_container is None:
                raise RuntimeError("DI container not initialized")
            return _di_container.resolve(StockApplicationService)

        stock_router.set_service_factory(stock_service_factory)
        logger.info("Dependency injection configured")

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

# Include routers
app.include_router(stock_router.router)


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
            "/stocks": "Stock management endpoints",
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
