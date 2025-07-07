"""Domain service exceptions - simplified starter kit.

Provides a focused set of exceptions with clear patterns for common
domain service error scenarios. Designed to teach best practices
for exception handling in domain-driven design.
"""

from typing import Any


class DomainServiceError(Exception):
    """Base exception for all domain service errors.

    Provides common error handling patterns with optional context details.
    All domain service exceptions should inherit from this class.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize domain service error with message and optional context.

        Args:
            message: Error message describing the problem
            context: Optional dictionary with additional error context
        """
        self.message = message
        self.context = context or {}
        super().__init__(message)


class ValidationError(DomainServiceError):
    """Raised when input validation fails.

    Use this when data doesn't meet business rules or format requirements.
    Includes optional field and value context for debugging.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
    ) -> None:
        """Initialize validation error with field and value context.

        Args:
            message: Validation error message
            field: Name of the field that failed validation
            value: Value that failed validation
        """
        context: dict[str, Any] = {}
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = str(value)
        super().__init__(message, context)


class CalculationError(DomainServiceError):
    """Raised when business calculations fail.

    Use this when mathematical operations cannot be completed
    due to invalid inputs, missing data, or calculation constraints.
    """

    def __init__(self, message: str, operation: str | None = None) -> None:
        """Initialize calculation error with operation context.

        Args:
            message: Calculation error message
            operation: Name of the calculation operation that failed
        """
        context: dict[str, Any] = {"operation": operation} if operation else {}
        super().__init__(message, context)


class InsufficientDataError(DomainServiceError):
    """Raised when required data is missing for operations.

    Use this when analysis or calculations cannot proceed
    due to missing required information.
    """

    def __init__(self, message: str, required_fields: list[str] | None = None) -> None:
        """Initialize insufficient data error with required fields context.

        Args:
            message: Error message describing missing data
            required_fields: List of field names that are required but missing
        """
        context: dict[str, Any] = {"required_fields": required_fields or []}
        super().__init__(message, context)
