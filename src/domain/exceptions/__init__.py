"""Domain exceptions module."""

from .base import (
    AlreadyExistsError,
    BusinessRuleViolationError,
    DomainError,
    NotFoundError,
)

__all__ = [
    "AlreadyExistsError",
    "BusinessRuleViolationError",
    "DomainError",
    "NotFoundError",
]
