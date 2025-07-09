"""Tests for portfolio-specific domain exceptions."""

from src.domain.exceptions.base import (
    AlreadyExistsError,
    BusinessRuleViolationError,
    NotFoundError,
)
from src.domain.exceptions.portfolio import (
    InactivePortfolioError,
    PortfolioAlreadyExistsError,
    PortfolioBalanceError,
    PortfolioNotFoundError,
)


class TestPortfolioNotFoundError:
    """Test cases for PortfolioNotFoundError."""

    def test_portfolio_not_found_inherits_from_not_found_error(self) -> None:
        """Test that PortfolioNotFoundError inherits from NotFoundError."""
        exception = PortfolioNotFoundError(identifier="portfolio-123")
        assert isinstance(exception, NotFoundError)
        assert isinstance(exception, Exception)

    def test_portfolio_not_found_with_id(self) -> None:
        """Test PortfolioNotFoundError with portfolio ID."""
        portfolio_id = "550e8400-e29b-41d4-a716-446655440000"
        exception = PortfolioNotFoundError(identifier=portfolio_id)
        assert exception.entity_type == "Portfolio"
        assert exception.identifier == portfolio_id
        assert str(exception) == f"Portfolio with identifier '{portfolio_id}' not found"

    def test_portfolio_not_found_with_name(self) -> None:
        """Test PortfolioNotFoundError with portfolio name."""
        exception = PortfolioNotFoundError(identifier="Main Portfolio")
        assert exception.entity_type == "Portfolio"
        assert exception.identifier == "Main Portfolio"
        assert str(exception) == "Portfolio with identifier 'Main Portfolio' not found"


class TestPortfolioAlreadyExistsError:
    """Test cases for PortfolioAlreadyExistsError."""

    def test_portfolio_already_exists_inherits_from_already_exists_error(self) -> None:
        """Test that PortfolioAlreadyExistsError inherits from AlreadyExistsError."""
        exception = PortfolioAlreadyExistsError(name="Retirement Fund")
        assert isinstance(exception, AlreadyExistsError)
        assert isinstance(exception, Exception)

    def test_portfolio_already_exists_with_name(self) -> None:
        """Test PortfolioAlreadyExistsError with portfolio name."""
        exception = PortfolioAlreadyExistsError(name="Growth Portfolio")
        assert exception.entity_type == "Portfolio"
        assert exception.identifier == "Growth Portfolio"
        assert (
            str(exception)
            == "Portfolio with identifier 'Growth Portfolio' already exists"
        )

    def test_portfolio_already_exists_stores_name(self) -> None:
        """Test PortfolioAlreadyExistsError stores name as attribute."""
        name = "Tech Stocks"
        exception = PortfolioAlreadyExistsError(name=name)
        assert exception.name == name


class TestInactivePortfolioError:
    """Test cases for InactivePortfolioError."""

    def test_inactive_portfolio_inherits_from_business_rule_violation(self) -> None:
        """Test InactivePortfolioError inherits from BusinessRuleViolationError."""
        exception = InactivePortfolioError(portfolio_id="portfolio-123")
        assert isinstance(exception, BusinessRuleViolationError)
        assert isinstance(exception, Exception)

    def test_inactive_portfolio_with_id(self) -> None:
        """Test InactivePortfolioError with portfolio ID."""
        portfolio_id = "portfolio-456"
        exception = InactivePortfolioError(portfolio_id=portfolio_id)
        assert exception.rule == "portfolio_must_be_active"
        assert exception.portfolio_id == portfolio_id
        expected_context = {
            "portfolio_id": portfolio_id,
            "operation": "modify",
        }
        assert exception.context == expected_context
        expected_msg = (
            "Business rule 'portfolio_must_be_active' violated. "
            "Context: {'portfolio_id': 'portfolio-456', 'operation': 'modify'}"
        )
        assert str(exception) == expected_msg

    def test_inactive_portfolio_with_custom_operation(self) -> None:
        """Test InactivePortfolioError with custom operation."""
        portfolio_id = "portfolio-789"
        operation = "add_position"
        exception = InactivePortfolioError(
            portfolio_id=portfolio_id,
            operation=operation,
        )
        assert exception.portfolio_id == portfolio_id
        assert exception.context is not None
        assert exception.context["operation"] == operation

    def test_inactive_portfolio_with_name(self) -> None:
        """Test InactivePortfolioError with portfolio name."""
        portfolio_id = "portfolio-123"
        portfolio_name = "Retired Portfolio"
        exception = InactivePortfolioError(
            portfolio_id=portfolio_id,
            portfolio_name=portfolio_name,
        )
        assert exception.portfolio_id == portfolio_id
        assert exception.portfolio_name == portfolio_name
        assert exception.context is not None
        assert exception.context["portfolio_name"] == portfolio_name


class TestPortfolioBalanceError:
    """Test cases for PortfolioBalanceError."""

    def test_portfolio_balance_inherits_from_business_rule_violation(self) -> None:
        """Test PortfolioBalanceError inherits from BusinessRuleViolationError."""
        exception = PortfolioBalanceError(
            portfolio_id="portfolio-123",
            required_amount=1000.0,
            available_amount=500.0,
        )
        assert isinstance(exception, BusinessRuleViolationError)
        assert isinstance(exception, Exception)

    def test_portfolio_balance_insufficient_funds(self) -> None:
        """Test PortfolioBalanceError for insufficient funds."""
        portfolio_id = "portfolio-123"
        required = 10000.0
        available = 5000.0
        exception = PortfolioBalanceError(
            portfolio_id=portfolio_id,
            required_amount=required,
            available_amount=available,
        )
        assert exception.rule == "sufficient_portfolio_balance"
        assert exception.portfolio_id == portfolio_id
        assert exception.required_amount == required
        assert exception.available_amount == available
        expected_context = {
            "portfolio_id": portfolio_id,
            "required_amount": required,
            "available_amount": available,
            "shortfall": required - available,
        }
        assert exception.context == expected_context

    def test_portfolio_balance_with_operation(self) -> None:
        """Test PortfolioBalanceError with operation context."""
        portfolio_id = "portfolio-456"
        required = 2500.0
        available = 1000.0
        operation = "buy_stock"
        exception = PortfolioBalanceError(
            portfolio_id=portfolio_id,
            required_amount=required,
            available_amount=available,
            operation=operation,
        )
        assert exception.context is not None
        assert exception.context["operation"] == operation
        assert exception.context["shortfall"] == 1500.0

    def test_portfolio_balance_zero_available(self) -> None:
        """Test PortfolioBalanceError with zero available balance."""
        exception = PortfolioBalanceError(
            portfolio_id="empty-portfolio",
            required_amount=100.0,
            available_amount=0.0,
        )
        assert exception.available_amount == 0.0
        assert exception.context is not None
        assert exception.context["shortfall"] == 100.0

    def test_portfolio_balance_negative_available(self) -> None:
        """Test PortfolioBalanceError with negative available balance."""
        exception = PortfolioBalanceError(
            portfolio_id="debt-portfolio",
            required_amount=500.0,
            available_amount=-200.0,
        )
        assert exception.available_amount == -200.0
        assert exception.context is not None
        assert exception.context["shortfall"] == 700.0


class TestPortfolioExceptionIntegration:
    """Integration tests for portfolio exceptions."""

    def test_all_portfolio_exceptions_have_consistent_behavior(self) -> None:
        """Test that all portfolio exceptions behave consistently."""
        not_found = PortfolioNotFoundError(identifier="portfolio-123")
        already_exists = PortfolioAlreadyExistsError(name="Test Portfolio")
        inactive = InactivePortfolioError(portfolio_id="portfolio-456")
        balance = PortfolioBalanceError(
            portfolio_id="portfolio-789",
            required_amount=1000.0,
            available_amount=500.0,
        )

        # All should be exceptions
        assert isinstance(not_found, Exception)
        assert isinstance(already_exists, Exception)
        assert isinstance(inactive, Exception)
        assert isinstance(balance, Exception)

        # All should have string representations
        assert str(not_found)
        assert str(already_exists)
        assert str(inactive)
        assert str(balance)

    def test_portfolio_exceptions_preserve_context(self) -> None:
        """Test that portfolio exceptions preserve important context."""
        portfolio_id = "test-portfolio"
        portfolio_name = "Test Portfolio"
        required = 5000.0
        available = 2000.0

        not_found = PortfolioNotFoundError(identifier=portfolio_id)
        already_exists = PortfolioAlreadyExistsError(name=portfolio_name)
        inactive = InactivePortfolioError(
            portfolio_id=portfolio_id,
            portfolio_name=portfolio_name,
        )
        balance = PortfolioBalanceError(
            portfolio_id=portfolio_id,
            required_amount=required,
            available_amount=available,
        )

        # Context should be accessible
        assert not_found.identifier == portfolio_id
        assert already_exists.name == portfolio_name
        assert inactive.portfolio_id == portfolio_id
        assert inactive.portfolio_name == portfolio_name
        assert balance.portfolio_id == portfolio_id
        assert balance.required_amount == required
        assert balance.available_amount == available
