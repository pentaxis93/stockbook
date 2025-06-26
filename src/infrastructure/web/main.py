"""
FastAPI application creation and configuration.

This module provides the factory function for creating FastAPI applications
with proper configuration and dependency injection integration.
"""

from fastapi import FastAPI

from src.infrastructure.web.routers.stock_router import reset_container
from src.infrastructure.web.routers.stock_router import router as stock_router


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        FastAPI application instance with proper configuration.
    """
    # Reset container for testing isolation
    reset_container()
    app = FastAPI(
        title="StockBook API",
        version="1.0.0",
        description=(
            "StockBook Personal Stock Trading Tracker API - "
            "Clean Architecture Edition with Domain-Driven Design"
        ),
        openapi_tags=[
            {
                "name": "stocks",
                "description": "Stock management operations",
            },
            {
                "name": "portfolios",
                "description": "Portfolio management operations",
            },
            {
                "name": "transactions",
                "description": "Transaction recording and management",
            },
            {
                "name": "health",
                "description": "System health and status checks",
            },
        ],
    )

    # Add health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:  # pyright: ignore[reportUnusedFunction]
        """
        Health check endpoint for monitoring system status.

        Returns:
            Dictionary with status and service information.
        """
        from datetime import datetime, timezone

        return {
            "status": "healthy",
            "service": "StockBook API",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

    # Include routers
    app.include_router(stock_router)

    return app


# Create app instance for uvicorn
app = create_app()
