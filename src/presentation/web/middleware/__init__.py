"""Web middleware for cross-cutting concerns.

This package contains middleware components for handling
common functionality across all web endpoints.
"""

from .error_handlers import handle_stock_errors

__all__ = ["handle_stock_errors"]
