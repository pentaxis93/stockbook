"""
Comprehensive tests for domain service exceptions.

Tests all exception classes to ensure proper initialization, inheritance,
context handling, and error messaging functionality.
"""

import pytest

from src.domain.services.exceptions import (
    CalculationError,
    DomainServiceError,
    InsufficientDataError,
    ValidationError,
)


class TestDomainServiceError:
    """Test cases for the base DomainServiceError class."""

    def test_initialization_with_message_only(self) -> None:
        """Should initialize with message and empty context."""
        error = DomainServiceError("Test error message")

        assert error.message == "Test error message"
        assert error.context == {}
        assert str(error) == "Test error message"

    def test_initialization_with_message_and_context(self) -> None:
        """Should initialize with message and provided context."""
        context = {"key1": "value1", "key2": 42}
        error = DomainServiceError("Test error", context)

        assert error.message == "Test error"
        assert error.context == context
        assert str(error) == "Test error"

    def test_initialization_with_none_context(self) -> None:
        """Should handle None context by creating empty dict."""
        error = DomainServiceError("Test error", None)

        assert error.message == "Test error"
        assert error.context == {}

    def test_inheritance_from_exception(self) -> None:
        """Should inherit from Exception class."""
        error = DomainServiceError("Test error")

        assert isinstance(error, Exception)

    def test_context_reference_behavior(self) -> None:
        """Should store reference to provided context dict."""
        original_context = {"key": "value"}
        error = DomainServiceError("Test error", original_context)

        # Verify context is stored as provided
        assert error.context is original_context

    def test_empty_message_handling(self) -> None:
        """Should handle empty message string."""
        error = DomainServiceError("")

        assert error.message == ""
        assert error.context == {}
        assert str(error) == ""


class TestValidationError:
    """Test cases for ValidationError class."""

    def test_initialization_with_message_only(self) -> None:
        """Should initialize with message and empty context."""
        error = ValidationError("Invalid input")

        assert error.message == "Invalid input"
        assert error.context == {}
        assert isinstance(error, DomainServiceError)

    def test_initialization_with_field_context(self) -> None:
        """Should include field in context when provided."""
        error = ValidationError("Invalid email format", field="email")

        assert error.message == "Invalid email format"
        assert error.context == {"field": "email"}

    def test_initialization_with_value_context(self) -> None:
        """Should include value in context when provided."""
        error = ValidationError("Invalid number", value=42)

        assert error.message == "Invalid number"
        assert error.context == {"value": "42"}

    def test_initialization_with_field_and_value_context(self) -> None:
        """Should include both field and value in context."""
        error = ValidationError("Invalid age", field="age", value=-5)

        assert error.message == "Invalid age"
        assert error.context == {"field": "age", "value": "-5"}

    def test_value_context_string_conversion(self) -> None:
        """Should convert value to string in context."""
        complex_value = [1, 2, {"key": "value"}]
        error = ValidationError("Invalid data", value=complex_value)

        assert error.context["value"] == str(complex_value)

    def test_none_value_context_excluded(self) -> None:
        """Should exclude value from context when None."""
        error = ValidationError("Test error", field="test", value=None)

        assert error.context == {"field": "test"}
        assert "value" not in error.context

    def test_inheritance_from_domain_service_error(self) -> None:
        """Should inherit from DomainServiceError."""
        error = ValidationError("Test validation error")

        assert isinstance(error, DomainServiceError)
        assert isinstance(error, Exception)


class TestCalculationError:
    """Test cases for CalculationError class."""

    def test_initialization_with_message_only(self) -> None:
        """Should initialize with message and empty context."""
        error = CalculationError("Division by zero")

        assert error.message == "Division by zero"
        assert error.context == {}
        assert isinstance(error, DomainServiceError)

    def test_initialization_with_operation_context(self) -> None:
        """Should include operation in context when provided."""
        error = CalculationError("Cannot calculate mean", operation="mean_calculation")

        assert error.message == "Cannot calculate mean"
        assert error.context == {"operation": "mean_calculation"}

    def test_initialization_with_none_operation(self) -> None:
        """Should handle None operation by creating empty context."""
        error = CalculationError("Calculation failed", operation=None)

        assert error.message == "Calculation failed"
        assert error.context == {}

    def test_empty_operation_string(self) -> None:
        """Should handle empty operation string as falsy and create empty context."""
        error = CalculationError("Math error", operation="")

        assert error.message == "Math error"
        assert error.context == {}

    def test_inheritance_from_domain_service_error(self) -> None:
        """Should inherit from DomainServiceError."""
        error = CalculationError("Test calculation error")

        assert isinstance(error, DomainServiceError)
        assert isinstance(error, Exception)


class TestInsufficientDataError:
    """Test cases for InsufficientDataError class."""

    def test_initialization_with_message_only(self) -> None:
        """Should initialize with message and empty required_fields list."""
        error = InsufficientDataError("Missing required data")

        assert error.message == "Missing required data"
        assert error.context == {"required_fields": []}
        assert isinstance(error, DomainServiceError)

    def test_initialization_with_required_fields(self) -> None:
        """Should include required_fields in context when provided."""
        fields = ["name", "email", "age"]
        error = InsufficientDataError("Missing user data", required_fields=fields)

        assert error.message == "Missing user data"
        assert error.context == {"required_fields": fields}

    def test_initialization_with_none_required_fields(self) -> None:
        """Should handle None required_fields by creating empty list."""
        error = InsufficientDataError("Data missing", required_fields=None)

        assert error.message == "Data missing"
        assert error.context == {"required_fields": []}

    def test_required_fields_list_reference_behavior(self) -> None:
        """Should store reference to original required_fields list."""
        original_fields = ["field1", "field2"]
        error = InsufficientDataError("Missing fields", required_fields=original_fields)

        # Verify that the same list reference is stored
        assert error.context["required_fields"] is original_fields

    def test_single_required_field(self) -> None:
        """Should handle single required field correctly."""
        error = InsufficientDataError("Missing price", required_fields=["price"])

        assert error.context == {"required_fields": ["price"]}

    def test_empty_required_fields_list(self) -> None:
        """Should handle empty required_fields list."""
        error = InsufficientDataError("No data", required_fields=[])

        assert error.context == {"required_fields": []}

    def test_inheritance_from_domain_service_error(self) -> None:
        """Should inherit from DomainServiceError."""
        error = InsufficientDataError("Test insufficient data error")

        assert isinstance(error, DomainServiceError)
        assert isinstance(error, Exception)


class TestExceptionHierarchy:
    """Test cases for exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_domain_service_error(self) -> None:
        """Should verify proper inheritance hierarchy."""
        validation_error = ValidationError("Validation error")
        calculation_error = CalculationError("Calculation error")
        insufficient_data_error = InsufficientDataError("Data error")

        assert isinstance(validation_error, DomainServiceError)
        assert isinstance(calculation_error, DomainServiceError)
        assert isinstance(insufficient_data_error, DomainServiceError)

    def test_all_exceptions_inherit_from_exception(self) -> None:
        """Should verify all exceptions inherit from base Exception."""
        base_error = DomainServiceError("Base error")
        validation_error = ValidationError("Validation error")
        calculation_error = CalculationError("Calculation error")
        insufficient_data_error = InsufficientDataError("Data error")

        assert isinstance(base_error, Exception)
        assert isinstance(validation_error, Exception)
        assert isinstance(calculation_error, Exception)
        assert isinstance(insufficient_data_error, Exception)

    def test_exception_can_be_caught_as_domain_service_error(self) -> None:
        """Should allow catching specific exceptions as base type."""
        # Test that specific exceptions can be caught as DomainServiceError
        msg = "Validation failed"
        with pytest.raises(DomainServiceError):
            raise ValidationError(msg)

        msg = "Calculation failed"
        with pytest.raises(DomainServiceError):
            raise CalculationError(msg)

        msg = "Data missing"
        with pytest.raises(DomainServiceError):
            raise InsufficientDataError(msg)

    def test_exception_can_be_caught_as_base_exception(self) -> None:
        """Should allow catching all exceptions as base Exception."""
        msg = "Base error"
        with pytest.raises(Exception, match="Base error"):
            raise DomainServiceError(msg)

        msg = "Validation error"
        with pytest.raises(Exception, match="Validation error"):
            raise ValidationError(msg)


class TestExceptionUsagePatterns:
    """Test cases for common exception usage patterns."""

    def test_validation_error_with_field_and_value_pattern(self) -> None:
        """Should support common validation error pattern."""
        # Simulate validation failure
        msg = "Stock symbol must be 1-10 characters"
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError(
                msg,
                field="symbol",
                value="VERY_LONG_SYMBOL_NAME",
            )

        assert "symbol" in exc_info.value.context["field"]
        assert "VERY_LONG_SYMBOL_NAME" in exc_info.value.context["value"]

    def test_calculation_error_with_operation_pattern(self) -> None:
        """Should support common calculation error pattern."""
        # Simulate calculation failure
        msg = "Cannot calculate portfolio value with negative holdings"
        with pytest.raises(CalculationError) as exc_info:
            raise CalculationError(
                msg,
                operation="portfolio_valuation",
            )

        assert exc_info.value.context["operation"] == "portfolio_valuation"

    def test_insufficient_data_error_with_multiple_fields_pattern(self) -> None:
        """Should support common insufficient data pattern."""
        # Simulate missing data error
        msg = "Cannot analyze portfolio without required data"
        with pytest.raises(InsufficientDataError) as exc_info:
            raise InsufficientDataError(
                msg,
                required_fields=["current_price", "shares", "purchase_date"],
            )

        required = exc_info.value.context["required_fields"]
        assert "current_price" in required
        assert "shares" in required
        assert "purchase_date" in required
        assert len(required) == 3
