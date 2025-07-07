"""Error handling middleware for web endpoints.

Provides decorators and utilities for consistent error handling
across all API endpoints.
"""

import functools
import logging
from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Type variable for decorator return type
F = TypeVar("F", bound=Callable[..., Any])

# Error message mappings for specific functions
ERROR_MESSAGES = {
    "get_stocks": "Failed to retrieve stocks",
    "update_stock": "Failed to update stock",
    "create_stock": "Failed to create stock",
}


def handle_stock_errors(func: F) -> F:
    """Decorator for handling common stock-related errors.

    Converts domain exceptions to appropriate HTTP responses:
    - ValueError with "already exists" -> 400 Bad Request
    - Other ValueError -> 422 Unprocessable Entity
    - All other exceptions -> 500 Internal Server Error

    Args:
        func: The endpoint function to decorate

    Returns:
        Wrapped function with error handling
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Execute function with error handling."""
        try:
            return await func(*args, **kwargs)

        except ValueError as e:
            error_msg = str(e)

            # Check if it's a not found error
            if "not found" in error_msg.lower():
                logger.warning("Resource not found: %s", error_msg)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_msg,
                ) from e

            # Check if it's a duplicate error
            if "already exists" in error_msg.lower():
                logger.warning("Duplicate resource error: %s", error_msg)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg,
                ) from e

            # Other ValueError = validation error
            logger.warning("Validation error: %s", error_msg)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg,
            ) from e

        except HTTPException:
            # Re-raise FastAPI exceptions as-is
            raise

        except Exception as e:
            # Log error based on function name for compatibility with tests
            if func.__name__ == "get_stocks":
                logger.exception("Error retrieving stocks")
            elif func.__name__ == "update_stock":
                logger.exception("Error updating stock")
            elif func.__name__ == "create_stock":
                logger.exception("Error creating stock")
            else:
                logger.exception("Unexpected error in %s", func.__name__)

            # Use function-specific error messages for compatibility
            detail = ERROR_MESSAGES.get(func.__name__, "An unexpected error occurred")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail,
            ) from e

    return wrapper  # type: ignore[return-value]
