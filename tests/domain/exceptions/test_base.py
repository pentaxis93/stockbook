"""Tests for base domain exceptions."""

from src.domain.exceptions.base import (
    AlreadyExistsError,
    BusinessRuleViolationError,
    DomainError,
    NotFoundError,
)


class TestDomainError:
    """Test cases for DomainException."""

    def test_domain_exception_is_base_exception(self) -> None:
        """Test that DomainError inherits from Exception."""
        exception = DomainError("Test error")
        assert isinstance(exception, Exception)
        assert str(exception) == "Test error"

    def test_domain_exception_with_custom_message(self) -> None:
        """Test DomainError with custom message."""
        message = "Custom domain error occurred"
        exception = DomainError(message)
        assert str(exception) == message


class TestNotFoundError:
    """Test cases for NotFoundError."""

    def test_not_found_exception_inheritance(self) -> None:
        """Test that NotFoundError inherits from DomainError."""
        exception = NotFoundError(entity_type="User", identifier="123")
        assert isinstance(exception, DomainError)
        assert isinstance(exception, Exception)

    def test_not_found_exception_attributes(self) -> None:
        """Test NotFoundError stores entity type and identifier."""
        entity_type = "Position"
        identifier = "ABC123"
        exception = NotFoundError(entity_type=entity_type, identifier=identifier)

        assert exception.entity_type == entity_type
        assert exception.identifier == identifier

    def test_not_found_exception_string_representation(self) -> None:
        """Test NotFoundError string representation."""
        exception = NotFoundError(entity_type="Stock", identifier="AAPL")
        assert str(exception) == "Stock with identifier 'AAPL' not found"

    def test_not_found_exception_with_numeric_identifier(self) -> None:
        """Test NotFoundError with numeric identifier."""
        exception = NotFoundError(entity_type="Transaction", identifier=12345)
        assert str(exception) == "Transaction with identifier '12345' not found"


class TestAlreadyExistsError:
    """Test cases for AlreadyExistsError."""

    def test_already_exists_exception_inheritance(self) -> None:
        """Test that AlreadyExistsError inherits from DomainError."""
        exception = AlreadyExistsError(
            entity_type="User",
            identifier="user@example.com",
        )
        assert isinstance(exception, DomainError)
        assert isinstance(exception, Exception)

    def test_already_exists_exception_attributes(self) -> None:
        """Test AlreadyExistsError stores entity type and identifier."""
        entity_type = "Position"
        identifier = "POS123"
        exception = AlreadyExistsError(
            entity_type=entity_type,
            identifier=identifier,
        )

        assert exception.entity_type == entity_type
        assert exception.identifier == identifier

    def test_already_exists_exception_string_representation(self) -> None:
        """Test AlreadyExistsError string representation."""
        exception = AlreadyExistsError(
            entity_type="Portfolio",
            identifier="main-portfolio",
        )
        assert (
            str(exception)
            == "Portfolio with identifier 'main-portfolio' already exists"
        )

    def test_already_exists_exception_with_uuid_identifier(self) -> None:
        """Test AlreadyExistsError with UUID identifier."""
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        exception = AlreadyExistsError(entity_type="Account", identifier=uuid_str)
        assert str(exception) == f"Account with identifier '{uuid_str}' already exists"


class TestBusinessRuleViolationError:
    """Test cases for BusinessRuleViolationError."""

    def test_business_rule_violation_exception_inheritance(self) -> None:
        """Test that BusinessRuleViolationError inherits from DomainError."""
        exception = BusinessRuleViolationError(
            rule="minimum_balance",
            context={"balance": -100, "minimum": 0},
        )
        assert isinstance(exception, DomainError)
        assert isinstance(exception, Exception)

    def test_business_rule_violation_exception_attributes(self) -> None:
        """Test BusinessRuleViolationError stores rule and context."""
        rule = "position_quantity_positive"
        context = {"quantity": -10, "ticker": "AAPL"}
        exception = BusinessRuleViolationError(rule=rule, context=context)

        assert exception.rule == rule
        assert exception.context == context

    def test_business_rule_violation_exception_string_representation(self) -> None:
        """Test BusinessRuleViolationError string representation."""
        exception = BusinessRuleViolationError(
            rule="insufficient_funds",
            context={"required": 1000, "available": 500},
        )
        expected = (
            "Business rule 'insufficient_funds' violated. "
            "Context: {'required': 1000, 'available': 500}"
        )
        assert str(exception) == expected

    def test_business_rule_violation_exception_without_context(self) -> None:
        """Test BusinessRuleViolationError without context."""
        exception = BusinessRuleViolationError(
            rule="invalid_operation",
            context=None,
        )
        assert str(exception) == "Business rule 'invalid_operation' violated"

    def test_business_rule_violation_exception_with_empty_context(self) -> None:
        """Test BusinessRuleViolationError with empty context."""
        exception = BusinessRuleViolationError(rule="invalid_state", context={})
        assert str(exception) == "Business rule 'invalid_state' violated"

    def test_business_rule_violation_exception_with_complex_context(self) -> None:
        """Test BusinessRuleViolationError with complex context."""
        context = {
            "position_id": "POS123",
            "current_quantity": 100,
            "requested_quantity": 150,
            "rules": ["max_position_size", "risk_limit"],
            "metadata": {"timestamp": "2024-01-01T00:00:00Z"},
        }
        exception = BusinessRuleViolationError(
            rule="position_limit_exceeded",
            context=context,
        )
        assert exception.rule == "position_limit_exceeded"
        assert exception.context == context
        assert "position_limit_exceeded" in str(exception)
        assert str(context) in str(exception)


class TestExceptionHierarchy:
    """Test the overall exception hierarchy."""

    def test_all_exceptions_inherit_from_domain_exception(self) -> None:
        """Test that all custom exceptions inherit from DomainError."""
        not_found = NotFoundError(entity_type="Test", identifier="123")
        already_exists = AlreadyExistsError(entity_type="Test", identifier="123")
        business_rule = BusinessRuleViolationError(rule="test_rule", context={})

        assert isinstance(not_found, DomainError)
        assert isinstance(already_exists, DomainError)
        assert isinstance(business_rule, DomainError)

    def test_exception_types_are_distinct(self) -> None:
        """Test that exception types are distinct from each other."""
        not_found = NotFoundError(entity_type="Test", identifier="123")
        already_exists = AlreadyExistsError(entity_type="Test", identifier="123")
        business_rule = BusinessRuleViolationError(rule="test_rule", context={})

        assert not isinstance(not_found, AlreadyExistsError)
        assert not isinstance(not_found, BusinessRuleViolationError)
        assert not isinstance(already_exists, NotFoundError)
        assert not isinstance(already_exists, BusinessRuleViolationError)
        assert not isinstance(business_rule, NotFoundError)
        assert not isinstance(business_rule, AlreadyExistsError)
