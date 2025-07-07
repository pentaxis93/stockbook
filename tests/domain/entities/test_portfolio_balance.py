"""
Tests for PortfolioBalance domain entity.

Following TDD approach with focus on value object purity and business logic.
Tests define expected behavior before implementation.
"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from src.domain.entities.portfolio_balance import PortfolioBalance
from src.domain.value_objects import IndexChange, Money


class TestPortfolioBalance:
    """Test PortfolioBalance domain entity with value objects and business logic."""

    def test_create_portfolio_balance_with_value_objects(self) -> None:
        """Test creating a portfolio balance with all value objects."""
        balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_withdrawals(Money(Decimal("500.00")))
            .with_deposits(Money(Decimal("1000.00")))
            .with_final_balance(Money(Decimal("10500.00")))
            .with_index_change(IndexChange(5.25))  # 5.25% change
            .build()
        )

        assert balance.portfolio_id == "portfolio-id-1"
        assert balance.balance_date == datetime(2024, 1, 15, tzinfo=UTC)
        assert balance.withdrawals.amount == Decimal("500.00")
        assert balance.deposits.amount == Decimal("1000.00")
        assert balance.final_balance.amount == Decimal("10500.00")
        assert balance.index_change is not None
        assert balance.index_change.value == 5.25

    def test_create_portfolio_balance_with_minimal_data(self) -> None:
        """Test creating portfolio balance with only required fields."""
        balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .build()
        )

        assert balance.portfolio_id == "portfolio-id-1"
        assert balance.balance_date == datetime(2024, 1, 15, tzinfo=UTC)
        assert balance.final_balance.amount == Decimal("10000.00")
        assert balance.withdrawals.amount == Decimal("0.00")  # Defaults to zero
        assert balance.deposits.amount == Decimal("0.00")  # Defaults to zero
        assert balance.index_change is None  # Defaults to None

    def test_create_portfolio_balance_with_none_optionals_allowed(self) -> None:
        """Should allow creating portfolio balance with None for optional fields."""
        balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .with_withdrawals(None)
            .with_deposits(None)
            .with_index_change(None)
            .build()
        )

        assert balance.withdrawals.amount == Decimal(
            "0.00",
        )  # Defaults to zero when None
        assert balance.deposits.amount == Decimal("0.00")  # Defaults to zero when None
        assert balance.index_change is None  # Remains None

    def test_create_portfolio_balance_with_invalid_portfolio_id_raises_error(
        self,
    ) -> None:
        """Should raise error for invalid portfolio ID."""
        with pytest.raises(ValueError, match="Portfolio ID must be a non-empty string"):
            _ = (
                PortfolioBalance.Builder()
                .with_portfolio_id("")  # Invalid empty string
                .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
                .with_final_balance(Money(Decimal("10000.00")))
                .build()
            )

    def test_create_portfolio_balance_with_invalid_index_change_raises_error(
        self,
    ) -> None:
        """Should raise error for invalid index change through IndexChange value
        object."""
        with pytest.raises(ValueError, match="Index change cannot exceed"):
            _ = IndexChange(
                150.0,
            )  # Error happens at IndexChange construction (over 100%)

    def test_portfolio_balance_equality(self) -> None:
        """Should compare portfolio balances based on ID."""
        balance1 = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .build()
        )

        balance2 = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("15000.00")))
            .build()
        )

        balance3 = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-2")
            .with_balance_date(datetime(2024, 1, 16, tzinfo=UTC))  # Different date
            .with_final_balance(Money(Decimal("10000.00")))
            .build()
        )

        # Different instances with same attributes but different IDs are NOT equal
        assert balance1 != balance2  # Different IDs
        assert balance1 != balance3  # Different IDs

        # Same ID means equal
        balance4 = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .with_id("same-id")
            .build()
        )
        balance5 = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-2")
            .with_balance_date(datetime(2024, 2, 20, tzinfo=UTC))  # Different date
            .with_final_balance(Money(Decimal("20000.00")))
            .with_withdrawals(Money(Decimal("1000.00")))
            .with_deposits(Money(Decimal("2000.00")))
            .with_index_change(IndexChange(5.5))
            .with_id("same-id")
            .build()
        )
        assert balance4 == balance5  # Same ID, even with different attributes

    def test_portfolio_balance_hash(self) -> None:
        """Should hash consistently based on ID."""
        balance1 = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .build()
        )

        balance2 = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("20000.00")))
            .build()
        )

        # Different IDs should have different hashes (likely but not guaranteed)
        assert hash(balance1) != hash(balance2)  # Different IDs

        # Same ID should have same hash
        balance3 = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .with_id("same-id")
            .build()
        )
        balance4 = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-2")
            .with_balance_date(datetime(2024, 2, 20, tzinfo=UTC))
            .with_final_balance(Money(Decimal("30000.00")))
            .with_withdrawals(Money(Decimal("5000.00")))
            .with_deposits(Money(Decimal("10000.00")))
            .with_index_change(IndexChange(-2.5))
            .with_id("same-id")
            .build()
        )
        assert hash(balance3) == hash(balance4)  # Same ID, same hash

    def test_portfolio_balance_string_representation(self) -> None:
        """Should have informative string representation."""
        balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10500.00")))
            .build()
        )

        assert "2024-01-15" in str(balance)
        assert "10500.00" in str(balance)

    def test_portfolio_balance_repr(self) -> None:
        """Should have detailed repr representation."""
        balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10500.00")))
            .build()
        )

        repr_str = repr(balance)
        assert "PortfolioBalance(portfolio_id=portfolio-id-1" in repr_str
        assert "date=2024-01-15 00:00:00+00:00)" in repr_str

    # Business behavior tests
    def test_portfolio_balance_calculate_net_flow(self) -> None:
        """Should calculate net cash flow (deposits - withdrawals)."""
        balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_withdrawals(Money(Decimal("500.00")))
            .with_deposits(Money(Decimal("1000.00")))
            .with_final_balance(Money(Decimal("10500.00")))
            .build()
        )

        net_flow = balance.calculate_net_flow()
        assert net_flow.amount == Decimal("500.00")  # 1000 - 500

    def test_portfolio_balance_has_positive_change(self) -> None:
        """Should check if portfolio has positive index change."""
        positive_balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10500.00")))
            .with_index_change(IndexChange(5.25))
            .build()
        )

        negative_balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("9500.00")))
            .with_index_change(IndexChange(-2.5))
            .build()
        )

        no_change_balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .build()
        )

        assert positive_balance.has_positive_change() is True
        assert negative_balance.has_positive_change() is False
        assert no_change_balance.has_positive_change() is False

    def test_portfolio_balance_has_negative_change(self) -> None:
        """Should check if portfolio has negative index change."""
        negative_balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("9500.00")))
            .with_index_change(IndexChange(-2.5))
            .build()
        )

        positive_balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10500.00")))
            .with_index_change(IndexChange(5.25))
            .build()
        )

        assert negative_balance.has_negative_change() is True
        assert positive_balance.has_negative_change() is False

    def test_portfolio_balance_had_deposits(self) -> None:
        """Should check if portfolio had deposits."""
        balance_with_deposits = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_deposits(Money(Decimal("1000.00")))
            .with_final_balance(Money(Decimal("10000.00")))
            .build()
        )

        balance_without_deposits = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .build()
        )

        assert balance_with_deposits.had_deposits() is True
        assert balance_without_deposits.had_deposits() is False

    def test_portfolio_balance_had_withdrawals(self) -> None:
        """Should check if portfolio had withdrawals."""
        balance_with_withdrawals = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_withdrawals(Money(Decimal("500.00")))
            .with_final_balance(Money(Decimal("10000.00")))
            .build()
        )

        balance_without_withdrawals = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .build()
        )

        assert balance_with_withdrawals.had_withdrawals() is True
        assert balance_without_withdrawals.had_withdrawals() is False

    def test_portfolio_balance_create_with_id(self) -> None:
        """Should create portfolio balance with provided ID."""
        test_id = "balance-id-123"
        balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .with_id(test_id)
            .build()
        )

        assert balance.id == test_id

    def test_portfolio_balance_id_immutability(self) -> None:
        """Should not be able to change ID after creation."""
        balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .with_id("test-id-1")
            .build()
        )

        # ID property should not have a setter
        with pytest.raises(AttributeError):
            balance.id = "different-id"  # type: ignore[misc]

    def test_portfolio_balance_from_persistence(self) -> None:
        """Should create portfolio balance from persistence with existing ID."""
        test_id = "persistence-id-456"
        balance = (
            PortfolioBalance.Builder()
            .with_id(test_id)
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .build()
        )

        assert balance.id == test_id

    def test_portfolio_balance_update_index_change(self) -> None:
        """Should be able to update index change."""
        balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .build()
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
            with pytest.raises(ValueError, match="Index change cannot exceed"):
                _ = IndexChange(change)

    def test_index_change_precision(self) -> None:
        """Test that index change values are properly rounded."""
        # Should round to 2 decimal places
        change = IndexChange(5.123456)
        assert change.value == 5.12

    def test_portfolio_balance_equality_with_non_portfolio_balance_object(self) -> None:
        """Test that portfolio balance equality returns False for
        non-PortfolioBalance objects."""

        balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .with_index_change(IndexChange(2.5))
            .build()
        )

        # Test equality with different types - should return False (covers line 114)
        assert balance != "not a balance"
        assert balance != 123
        assert balance is not None
        assert balance != {
            "portfolio_id": "portfolio-1",
            "balance_date": datetime(2024, 1, 15, tzinfo=UTC),
        }


class TestPortfolioBalanceBuilder:
    """Test cases for PortfolioBalance.Builder pattern."""

    def test_builder_creates_portfolio_balance_with_all_fields(self) -> None:
        """Test that Builder can create a portfolio balance with all fields."""
        balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10500.00")))
            .with_withdrawals(Money(Decimal("500.00")))
            .with_deposits(Money(Decimal("1000.00")))
            .with_index_change(IndexChange(5.25))
            .with_id("balance-id")
            .build()
        )

        assert balance.portfolio_id == "portfolio-1"
        assert balance.balance_date == datetime(2024, 1, 15, tzinfo=UTC)
        assert balance.final_balance.amount == Decimal("10500.00")
        assert balance.withdrawals.amount == Decimal("500.00")
        assert balance.deposits.amount == Decimal("1000.00")
        assert balance.index_change is not None
        assert balance.index_change.value == 5.25
        assert balance.id == "balance-id"

    def test_builder_creates_portfolio_balance_with_minimal_fields(self) -> None:
        """Test that Builder can create a portfolio balance with only required
        fields."""
        balance = (
            PortfolioBalance.Builder()
            .with_portfolio_id("portfolio-1")
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
            .build()
        )

        assert balance.portfolio_id == "portfolio-1"
        assert balance.balance_date == datetime(2024, 1, 15, tzinfo=UTC)
        assert balance.final_balance.amount == Decimal("10000.00")
        assert balance.withdrawals.amount == Decimal("0")  # Default
        assert balance.deposits.amount == Decimal("0")  # Default
        assert balance.index_change is None

    def test_builder_raises_error_when_required_fields_missing(self) -> None:
        """Test that Builder raises error when required fields are missing."""
        # Missing portfolio_id
        with pytest.raises(ValueError, match="Portfolio ID is required"):
            _ = (
                PortfolioBalance.Builder()
                .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
                .with_final_balance(Money(Decimal("10000.00")))
                .build()
            )

        # Missing balance_date
        with pytest.raises(ValueError, match="Balance date is required"):
            _ = (
                PortfolioBalance.Builder()
                .with_portfolio_id("portfolio-1")
                .with_final_balance(Money(Decimal("10000.00")))
                .build()
            )

        # Missing final_balance
        with pytest.raises(ValueError, match="Final balance is required"):
            _ = (
                PortfolioBalance.Builder()
                .with_portfolio_id("portfolio-1")
                .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
                .build()
            )

    def test_builder_validates_portfolio_id(self) -> None:
        """Test that Builder validates portfolio_id."""
        builder = (
            PortfolioBalance.Builder()
            .with_balance_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_final_balance(Money(Decimal("10000.00")))
        )

        # Empty string should raise error
        with pytest.raises(ValueError, match="Portfolio ID must be a non-empty string"):
            _ = builder.with_portfolio_id("").build()

    def test_builder_method_chaining(self) -> None:
        """Test that all builder methods return self for chaining."""
        builder = PortfolioBalance.Builder()

        assert builder.with_portfolio_id("p1") is builder
        assert builder.with_balance_date(datetime(2024, 1, 15, tzinfo=UTC)) is builder
        assert builder.with_final_balance(Money(Decimal("10000.00"))) is builder
        assert builder.with_withdrawals(Money(Decimal("500.00"))) is builder
        assert builder.with_deposits(Money(Decimal("1000.00"))) is builder
        assert builder.with_index_change(IndexChange(5.25)) is builder
        assert builder.with_id("id1") is builder
