"""Domain exception handler middleware.

Maps domain exceptions to appropriate HTTP responses with consistent error format.
"""

import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions.base import (
    AlreadyExistsError,
    BusinessRuleViolationError,
    DomainError,
    NotFoundError,
)

logger = logging.getLogger(__name__)


async def not_found_exception_handler(
    _request: Request,
    exception: NotFoundError,
) -> JSONResponse:
    """Handle NotFoundError exceptions.

    Maps domain NotFoundError to HTTP 404 response.

    Args:
        _request: The FastAPI request object
        exception: The NotFoundError exception

    Returns:
        JSONResponse with 404 status code
    """
    return JSONResponse(
        status_code=404,
        content={"detail": str(exception)},
    )


async def already_exists_exception_handler(
    _request: Request,
    exception: AlreadyExistsError,
) -> JSONResponse:
    """Handle AlreadyExistsError exceptions.

    Maps domain AlreadyExistsError to HTTP 409 Conflict response.

    Args:
        _request: The FastAPI request object
        exception: The AlreadyExistsError exception

    Returns:
        JSONResponse with 409 status code
    """
    return JSONResponse(
        status_code=409,
        content={"detail": str(exception)},
    )


async def business_rule_violation_exception_handler(
    _request: Request,
    exception: BusinessRuleViolationError,
) -> JSONResponse:
    """Handle BusinessRuleViolationError exceptions.

    Maps domain BusinessRuleViolationError to HTTP 422 Unprocessable Entity response.

    Args:
        _request: The FastAPI request object
        exception: The BusinessRuleViolationError exception

    Returns:
        JSONResponse with 422 status code
    """
    return JSONResponse(
        status_code=422,
        content={"detail": str(exception)},
    )


async def domain_exception_handler(
    _request: Request,
    exception: DomainError,
) -> JSONResponse:
    """Handle generic DomainError exceptions.

    Maps generic domain errors to HTTP 400 Bad Request response.

    Args:
        _request: The FastAPI request object
        exception: The DomainError exception

    Returns:
        JSONResponse with 400 status code
    """
    return JSONResponse(
        status_code=400,
        content={"detail": str(exception)},
    )


async def http_exception_handler(
    _request: Request,
    exception: HTTPException,
) -> JSONResponse:
    """Handle HTTPException pass-through.

    Preserves the original HTTPException without modification.

    Args:
        _request: The FastAPI request object
        exception: The HTTPException

    Returns:
        JSONResponse with the original status code and detail
    """
    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": exception.detail},
        headers=getattr(exception, "headers", None),
    )


async def generic_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Handle unexpected exceptions.

    Maps any unexpected exception to HTTP 500 Internal Server Error.
    Logs the exception details for debugging.

    Args:
        request: The FastAPI request object
        exception: Any unexpected exception

    Returns:
        JSONResponse with 500 status code
    """
    # Log the exception with request path for debugging
    logger.exception(
        "Unexpected error at %s: %s",
        request.url.path,
        str(exception),
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )
