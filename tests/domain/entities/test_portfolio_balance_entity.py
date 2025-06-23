"""
Tests for PortfolioBalanceEntity domain entity.

Following TDD approach with focus on value object purity and business logic.
Tests define expected behavior before implementation.
"""

from datetime import date
from decimal import Decimal

import pytest

from src.domain.entities.portfolio_balance_entity import PortfolioBalanceEntity
from src.domain.value_objects import IndexChange, Money


class TestPortfolioBalanceEntity:
    """Test PortfolioBalanceEntity domain entity with value objects and business logic."""

    def test_create_portfolio_balance_with_value_objects(self) -> None:
        """Test creating a portfolio balance with all value objects."""
        balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            withdrawals=Money(Decimal("500.00")),
            deposits=Money(Decimal("1000.00")),
            final_balance=Money(Decimal("10500.00")),
            index_change=IndexChange(5.25),  # 5.25% change
        )

        assert balance.portfolio_id == "portfolio-id-1"
        assert balance.balance_date == date(2024, 1, 15)
        assert balance.withdrawals.amount == Decimal("500.00")
        assert balance.deposits.amount == Decimal("1000.00")
        assert balance.final_balance.amount == Decimal("10500.00")
        assert balance.index_change is not None
        assert balance.index_change.value == 5.25

    def test_create_portfolio_balance_with_minimal_data(self) -> None:
        """Test creating portfolio balance with only required fields."""
        balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        assert balance.portfolio_id == "portfolio-id-1"
        assert balance.balance_date == date(2024, 1, 15)
        assert balance.final_balance.amount == Decimal("10000.00")
        assert balance.withdrawals.amount == Decimal("0.00")  # Defaults to zero
        assert balance.deposits.amount == Decimal("0.00")  # Defaults to zero
        assert balance.index_change is None  # Defaults to None

    def test_create_portfolio_balance_with_none_optionals_allowed(self) -> None:
        """Should allow creating portfolio balance with None for optional fields."""
        balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
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

    def test_create_portfolio_balance_with_invalid_portfolio_id_raises_error(
        self,
    ) -> None:
        """Should raise error for invalid portfolio ID."""
        with pytest.raises(ValueError, match="Portfolio ID must be a non-empty string"):
            _ = PortfolioBalanceEntity(
                portfolio_id="",  # Invalid empty string
                balance_date=date(2024, 1, 15),
                final_balance=Money(Decimal("10000.00")),
            )

    def test_create_portfolio_balance_with_invalid_index_change_raises_error(
        self,
    ) -> None:
        """Should raise error for invalid index change through IndexChange value object."""
        with pytest.raises(ValueError, match="Index change cannot exceed"):
            _ = IndexChange(
                150.0
            )  # Error happens at IndexChange construction (over 100%)

    def test_portfolio_balance_equality(self) -> None:
        """Should compare portfolio balances based on business identity (portfolio_id, date)."""
        balance1 = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        balance2 = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("15000.00")),  # Different amount
        )

        balance3 = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-2",  # Different portfolio
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        assert balance1 == balance2  # Same portfolio and date
        assert balance1 != balance3  # Different portfolio

    def test_portfolio_balance_hash(self) -> None:
        """Should hash consistently based on business identity."""
        balance1 = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        balance2 = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("20000.00")),  # Different amount
        )

        assert hash(balance1) == hash(balance2)  # Same portfolio and date

    def test_portfolio_balance_string_representation(self) -> None:
        """Should have informative string representation."""
        balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10500.00")),
        )

        assert "2024-01-15" in str(balance)
        assert "10500.00" in str(balance)

    def test_portfolio_balance_repr(self) -> None:
        """Should have detailed repr representation."""
        balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10500.00")),
        )

        expected = (
            "PortfolioBalanceEntity(portfolio_id=portfolio-id-1, date=2024-01-15)"
        )
        assert repr(balance) == expected

    # Business behavior tests
    def test_portfolio_balance_calculate_net_flow(self) -> None:
        """Should calculate net cash flow (deposits - withdrawals)."""
        balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            withdrawals=Money(Decimal("500.00")),
            deposits=Money(Decimal("1000.00")),
            final_balance=Money(Decimal("10500.00")),
        )

        net_flow = balance.calculate_net_flow()
        assert net_flow.amount == Decimal("500.00")  # 1000 - 500

    def test_portfolio_balance_has_positive_change(self) -> None:
        """Should check if portfolio has positive index change."""
        positive_balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10500.00")),
            index_change=IndexChange(5.25),
        )

        negative_balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("9500.00")),
            index_change=IndexChange(-2.5),
        )

        no_change_balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        assert positive_balance.has_positive_change() is True
        assert negative_balance.has_positive_change() is False
        assert no_change_balance.has_positive_change() is False

    def test_portfolio_balance_has_negative_change(self) -> None:
        """Should check if portfolio has negative index change."""
        negative_balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("9500.00")),
            index_change=IndexChange(-2.5),
        )

        positive_balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10500.00")),
            index_change=IndexChange(5.25),
        )

        assert negative_balance.has_negative_change() is True
        assert positive_balance.has_negative_change() is False

    def test_portfolio_balance_had_deposits(self) -> None:
        """Should check if portfolio had deposits."""
        balance_with_deposits = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            deposits=Money(Decimal("1000.00")),
            final_balance=Money(Decimal("10000.00")),
        )

        balance_without_deposits = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        assert balance_with_deposits.had_deposits() is True
        assert balance_without_deposits.had_deposits() is False

    def test_portfolio_balance_had_withdrawals(self) -> None:
        """Should check if portfolio had withdrawals."""
        balance_with_withdrawals = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            withdrawals=Money(Decimal("500.00")),
            final_balance=Money(Decimal("10000.00")),
        )

        balance_without_withdrawals = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        assert balance_with_withdrawals.had_withdrawals() is True
        assert balance_without_withdrawals.had_withdrawals() is False

    def test_portfolio_balance_create_with_id(self) -> None:
        """Should create portfolio balance with provided ID."""
        test_id = "balance-id-123"
        balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
            id=test_id,
        )

        assert balance.id == test_id

    def test_portfolio_balance_id_immutability(self) -> None:
        """Should not be able to change ID after creation."""
        balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
            id="test-id-1",
        )

        # ID property should not have a setter
        with pytest.raises(AttributeError):
            balance.id = "different-id"  # type: ignore[misc]

    def test_portfolio_balance_from_persistence(self) -> None:
        """Should create portfolio balance from persistence with existing ID."""
        test_id = "persistence-id-456"
        balance = PortfolioBalanceEntity.from_persistence(
            test_id,
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        assert balance.id == test_id

    def test_portfolio_balance_update_index_change(self) -> None:
        """Should be able to update index change."""
        balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
        )

        # Update with IndexChange value object
        balance.update_index_change(IndexChange(7.5))
        assert balance.index_change is not None
        assert balance.index_change.value == 7.5

        # Update with float (should be converted to IndexChange)
        balance.update_index_change(3.25)
        assert balance.index_change is not None
        assert balance.index_change.value == 3.25

        # Update with None
        balance.update_index_change(None)
        assert balance.index_change is None


class TestIndexChange:
    """Test IndexChange value object validation."""

    def test_valid_index_changes_accepted(self) -> None:
        """Test that valid index changes are accepted."""
        valid_changes = [0.0, 5.25, -2.5, 50.0, -25.0, 99.99, -99.99]
        for change in valid_changes:
            index_change = IndexChange(change)
            assert index_change.value == change

    def test_extreme_index_changes_rejected(self) -> None:
        """Test that extreme index changes are rejected."""
        extreme_changes = [150.0, -150.0, 200.0, -200.0]
        for change in extreme_changes:
            with pytest.raises(ValueError):
                _ = IndexChange(change)

    def test_index_change_precision(self) -> None:
        """Test that index change values are properly rounded."""
        # Should round to 2 decimal places
        change = IndexChange(5.123456)
        assert change.value == 5.12

    def test_portfolio_balance_equality_with_non_portfolio_balance_object(self) -> None:
        """Test that portfolio balance equality returns False for non-PortfolioBalanceEntity objects."""

        balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-1",
            balance_date=date(2024, 1, 15),
            final_balance=Money(Decimal("10000.00")),
            index_change=IndexChange(2.5),
        )

        # Test equality with different types - should return False (covers line 114)
        assert balance != "not a balance"
        assert balance != 123
        assert balance != None
        assert balance != {
            "portfolio_id": "portfolio-1",
            "balance_date": date(2024, 1, 15),
        }
