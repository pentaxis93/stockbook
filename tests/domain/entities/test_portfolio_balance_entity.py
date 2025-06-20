"""
Tests for PortfolioBalanceEntity domain entity.

Following TDD approach with focus on value object purity and business logic.
Tests define expected behavior before implementation.
"""

from datetime import date
from decimal import Decimal

import pytest

from src.domain.entities.portfolio_balance_entity import PortfolioBalanceEntity
from src.domain.value_objects import Money


class TestPortfolioBalanceEntity:
    """Test PortfolioBalanceEntity domain entity with value objects and business logic."""

    def test_create_portfolio_balance_with_value_objects(self):
        """Test creating a portfolio balance with all value objects."""
        from src.domain.value_objects import IndexChange

        balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            withdrawals=Money(Decimal("500.00")),
            deposits=Money(Decimal("1000.00")),
            final_balance=Money(Decimal("10500.00")),
            index_change=IndexChange(5.25),  # 5.25% change
        )

        assert balance.portfolio_id == 1
        assert balance.balance_date == date(2024, 1, 15)
        assert balance.withdrawals.amount == Decimal("500.00")
        assert balance.deposits.amount == Decimal("1000.00")
        assert balance.final_balance.amount == Decimal("10500.00")
        assert balance.index_change.value == 5.25

    def test_create_portfolio_balance_with_minimal_data(self):
        """Test creating portfolio balance with only required fields."""
        balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        assert balance.portfolio_id == 1
        assert balance.balance_date == date(2024, 1, 15)
        assert balance.final_balance.amount == Decimal("10000.00")
        assert balance.withdrawals.amount == Decimal("0.00")  # Defaults to zero
        assert balance.deposits.amount == Decimal("0.00")  # Defaults to zero
        assert balance.index_change is None  # Defaults to None

    def test_create_portfolio_balance_with_none_optionals_allowed(self):
        """Should allow creating portfolio balance with None for optional fields."""
        balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
            withdrawals=None,
            deposits=None,
            index_change=None,
        )

        assert balance.withdrawals.amount == Decimal(
            "0.00"
        )  # Defaults to zero when None
        assert balance.deposits.amount == Decimal("0.00")  # Defaults to zero when None
        assert balance.index_change is None  # Remains None

    def test_create_portfolio_balance_with_invalid_portfolio_id_raises_error(self):
        """Should raise error for invalid portfolio ID."""
        with pytest.raises(ValueError, match="Portfolio ID must be positive"):
            PortfolioBalanceEntity(
                portfolio_id=0,  # Invalid
                balance_date=date(2024, 1, 15),
                final_balance=Money(Decimal("10000.00")),
            )

    def test_create_portfolio_balance_with_invalid_index_change_raises_error(self):
        """Should raise error for invalid index change through IndexChange value object."""
        from src.domain.value_objects import IndexChange

        with pytest.raises(ValueError, match="Index change cannot exceed"):
            IndexChange(150.0)  # Error happens at IndexChange construction (over 100%)

    def test_portfolio_balance_equality(self):
        """Should compare portfolio balances based on business identity (portfolio_id, date)."""
        balance1 = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        balance2 = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("15000.00")),  # Different amount
        )

        balance3 = PortfolioBalanceEntity(
            portfolio_id=2,  # Different portfolio
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        assert balance1 == balance2  # Same portfolio and date
        assert balance1 != balance3  # Different portfolio

    def test_portfolio_balance_hash(self):
        """Should hash consistently based on business identity."""
        balance1 = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        balance2 = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("20000.00")),  # Different amount
        )

        assert hash(balance1) == hash(balance2)  # Same portfolio and date

    def test_portfolio_balance_string_representation(self):
        """Should have informative string representation."""
        balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10500.00")),
        )

        assert "2024-01-15" in str(balance)
        assert "10500.00" in str(balance)

    def test_portfolio_balance_repr(self):
        """Should have detailed repr representation."""
        balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10500.00")),
        )

        expected = "PortfolioBalanceEntity(portfolio_id=1, date=2024-01-15)"
        assert repr(balance) == expected

    # Business behavior tests
    def test_portfolio_balance_calculate_net_flow(self):
        """Should calculate net cash flow (deposits - withdrawals)."""
        balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            withdrawals=Money(Decimal("500.00")),
            deposits=Money(Decimal("1000.00")),
            final_balance=Money(Decimal("10500.00")),
        )

        net_flow = balance.calculate_net_flow()
        assert net_flow.amount == Decimal("500.00")  # 1000 - 500

    def test_portfolio_balance_has_positive_change(self):
        """Should check if portfolio has positive index change."""
        from src.domain.value_objects import IndexChange

        positive_balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10500.00")),
            index_change=IndexChange(5.25),
        )

        negative_balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("9500.00")),
            index_change=IndexChange(-2.5),
        )

        no_change_balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        assert positive_balance.has_positive_change() is True
        assert negative_balance.has_positive_change() is False
        assert no_change_balance.has_positive_change() is False

    def test_portfolio_balance_has_negative_change(self):
        """Should check if portfolio has negative index change."""
        from src.domain.value_objects import IndexChange

        negative_balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("9500.00")),
            index_change=IndexChange(-2.5),
        )

        positive_balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10500.00")),
            index_change=IndexChange(5.25),
        )

        assert negative_balance.has_negative_change() is True
        assert positive_balance.has_negative_change() is False

    def test_portfolio_balance_had_deposits(self):
        """Should check if portfolio had deposits."""
        balance_with_deposits = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            deposits=Money(Decimal("1000.00")),
            final_balance=Money(Decimal("10000.00")),
        )

        balance_without_deposits = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        assert balance_with_deposits.had_deposits() is True
        assert balance_without_deposits.had_deposits() is False

    def test_portfolio_balance_had_withdrawals(self):
        """Should check if portfolio had withdrawals."""
        balance_with_withdrawals = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            withdrawals=Money(Decimal("500.00")),
            final_balance=Money(Decimal("10000.00")),
        )

        balance_without_withdrawals = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        assert balance_with_withdrawals.had_withdrawals() is True
        assert balance_without_withdrawals.had_withdrawals() is False

    def test_portfolio_balance_set_id(self):
        """Should allow setting balance ID."""
        balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        balance.set_id(123)
        assert balance.id == 123

    def test_portfolio_balance_set_id_with_invalid_id_raises_error(self):
        """Should raise error when setting invalid ID."""
        balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        with pytest.raises(ValueError, match="ID must be a positive integer"):
            balance.set_id(0)

    def test_portfolio_balance_set_id_when_already_set_raises_error(self):
        """Should raise error when trying to change existing ID."""
        balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
            balance_id=123,
        )

        with pytest.raises(ValueError, match="ID is already set and cannot be changed"):
            balance.set_id(456)

    def test_portfolio_balance_update_index_change(self):
        """Should be able to update index change."""
        from src.domain.value_objects import IndexChange

        balance = PortfolioBalanceEntity(
            portfolio_id=1,
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        # Update with IndexChange value object
        balance.update_index_change(IndexChange(7.5))
        assert balance.index_change.value == 7.5

        # Update with float (should be converted to IndexChange)
        balance.update_index_change(3.25)
        assert balance.index_change.value == 3.25

        # Update with None
        balance.update_index_change(None)
        assert balance.index_change is None


class TestIndexChange:
    """Test IndexChange value object validation."""

    def test_valid_index_changes_accepted(self):
        """Test that valid index changes are accepted."""
        from src.domain.value_objects import IndexChange

        valid_changes = [0.0, 5.25, -2.5, 50.0, -25.0, 99.99, -99.99]
        for change in valid_changes:
            index_change = IndexChange(change)
            assert index_change.value == change

    def test_extreme_index_changes_rejected(self):
        """Test that extreme index changes are rejected."""
        from src.domain.value_objects import IndexChange

        extreme_changes = [150.0, -150.0, 200.0, -200.0]
        for change in extreme_changes:
            with pytest.raises(ValueError):
                IndexChange(change)

    def test_index_change_precision(self):
        """Test that index change values are properly rounded."""
        from src.domain.value_objects import IndexChange

        # Should round to 2 decimal places
        change = IndexChange(5.123456)
        assert change.value == 5.12
