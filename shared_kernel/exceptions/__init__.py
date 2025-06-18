"""
Shared exception hierarchy used across bounded contexts.

Contains foundational exceptions that provide consistent error handling
patterns across all domains.
"""

from .domain_exceptions import (
    AnalysisError,
    BusinessRuleViolationError,
    CalculationError,
    DomainServiceError,
    InsufficientDataError,
    ValidationError,
)

__all__ = [
    "DomainServiceError",
    "ValidationError",
    "BusinessRuleViolationError",
    "CalculationError",
    "InsufficientDataError",
    "AnalysisError",
]
