"""
Exceptions for domain services.

Provides specialized exceptions for different types of domain service errors
with clear error messages and appropriate error handling context.
"""

from typing import Any, List, Optional


class DomainServiceError(Exception):
    """Base exception for all domain service errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ValidationError(DomainServiceError):
    """Raised when validation rules are violated."""

    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        self.field = field
        self.value = value
        super().__init__(message, {"field": field, "value": value})


class BusinessRuleViolationError(DomainServiceError):
    """Raised when business rules are violated."""

    def __init__(self, message: str, rule_name: str, context: Optional[dict] = None):
        self.rule_name = rule_name
        self.context = context or {}
        super().__init__(message, {"rule": rule_name, "context": context})


class CalculationError(DomainServiceError):
    """Raised when calculations cannot be performed or produce invalid results."""

    def __init__(
        self, message: str, calculation_type: str, input_data: Optional[dict] = None
    ):
        self.calculation_type = calculation_type
        self.input_data = input_data or {}
        super().__init__(
            message, {"calculation_type": calculation_type, "input_data": input_data}
        )


class InsufficientDataError(DomainServiceError):
    """Raised when insufficient data is available for analysis or calculations."""

    def __init__(
        self,
        message: str,
        required_data: List[str],
        available_data: Optional[List[str]] = None,
    ):
        self.required_data = required_data
        self.available_data = available_data or []
        super().__init__(
            message, {"required": required_data, "available": available_data}
        )


class PricingError(DomainServiceError):
    """Raised when price-related calculations or validations fail."""

    def __init__(
        self,
        message: str,
        symbol: Optional[str] = None,
        price_value: Optional[str] = None,
    ):
        self.symbol = symbol
        self.price_value = price_value
        super().__init__(message, {"symbol": symbol, "price": price_value})


class InvalidPriceDataError(PricingError):
    """Raised when price data is invalid or corrupted."""

    pass


class RiskAnalysisError(DomainServiceError):
    """Raised when risk analysis cannot be completed."""

    def __init__(
        self,
        message: str,
        risk_type: Optional[str] = None,
        analysis_context: Optional[dict] = None,
    ):
        self.risk_type = risk_type
        self.analysis_context = analysis_context or {}
        super().__init__(message, {"risk_type": risk_type, "context": analysis_context})


class AnalysisError(DomainServiceError):
    """Raised when general analysis operations fail."""

    pass
