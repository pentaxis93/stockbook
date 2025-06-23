"""
FastAPI application creation and configuration.

This module provides the factory function for creating FastAPI applications
with proper configuration and dependency injection integration.
"""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        FastAPI application instance with proper configuration.
    """
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

    return app
