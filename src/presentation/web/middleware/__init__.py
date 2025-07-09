"""Web middleware for cross-cutting concerns.

This package contains middleware components for handling
common functionality across all web endpoints.
"""

# Domain exception handlers are now imported from exception_handler module
from .exception_handler import (
    already_exists_exception_handler,
    business_rule_violation_exception_handler,
    domain_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    not_found_exception_handler,
)

__all__ = [
    "already_exists_exception_handler",
    "business_rule_violation_exception_handler",
    "domain_exception_handler",
    "generic_exception_handler",
    "http_exception_handler",
    "not_found_exception_handler",
]
