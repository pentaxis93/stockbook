"""
Shared exception hierarchy used across bounded contexts.

Contains foundational exceptions that provide consistent error handling
patterns across all domains.
"""

from .domain_exceptions import (
    DomainServiceError,
    ValidationError,
    BusinessRuleViolationError,
    CalculationError,
    InsufficientDataError,
    AnalysisError,
)

__all__ = [
    "DomainServiceError",
    "ValidationError",
    "BusinessRuleViolationError",
    "CalculationError",
    "InsufficientDataError",
    "AnalysisError",
]
