"""Tests for Position domain entity."""

from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from src.domain.entities.position import Position
from src.domain.value_objects.money import Money
from src.domain.value_objects.quantity import Quantity

UTC = ZoneInfo("UTC")


class TestPositionBuilder:
    """Test cases for Position.Builder pattern."""

    def test_builder_creates_position_with_all_fields(self) -> None:
        """Test that Builder can create a position with all fields."""
        last_transaction_date = datetime(2024, 1, 15, tzinfo=UTC)

        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.25")))
            .with_last_transaction_date(last_transaction_date)
            .with_id("position-id")
            .build()
        )

        assert position.portfolio_id == "portfolio-1"
        assert position.stock_id == "stock-1"
        assert position.quantity.value == 100
        assert position.average_cost.amount == Decimal("150.25")
        assert position.last_transaction_date == last_transaction_date
        assert position.id == "position-id"

    def test_builder_creates_position_with_minimal_fields(self) -> None:
        """Test that Builder can create a position with only required fields."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-1")
            .with_quantity(Quantity(50))
            .with_average_cost(Money(Decimal("175.50")))
            .build()
        )

        assert position.portfolio_id == "portfolio-1"
        assert position.stock_id == "stock-1"
        assert position.quantity.value == 50
        assert position.average_cost.amount == Decimal("175.50")
        assert position.last_transaction_date is None
        assert position.id is not None  # Generated UUID

    def test_builder_raises_error_when_required_fields_missing(self) -> None:
        """Test that Builder raises error when required fields are missing."""
        # Missing portfolio_id
        with pytest.raises(ValueError, match="Portfolio ID is required"):
            _ = (
                Position.Builder()
                .with_stock_id("stock-1")
                .with_quantity(Quantity(100))
                .with_average_cost(Money(Decimal("100.00")))
                .build()
            )

        # Missing stock_id
        with pytest.raises(ValueError, match="Stock ID is required"):
            _ = (
                Position.Builder()
                .with_portfolio_id("portfolio-1")
                .with_quantity(Quantity(100))
                .with_average_cost(Money(Decimal("100.00")))
                .build()
            )

        # Missing quantity
        with pytest.raises(ValueError, match="Quantity is required"):
            _ = (
                Position.Builder()
                .with_portfolio_id("portfolio-1")
                .with_stock_id("stock-1")
                .with_average_cost(Money(Decimal("100.00")))
                .build()
            )

        # Missing average_cost
        with pytest.raises(ValueError, match="Average cost is required"):
            _ = (
                Position.Builder()
                .with_portfolio_id("portfolio-1")
                .with_stock_id("stock-1")
                .with_quantity(Quantity(100))
                .build()
            )

    def test_builder_validates_empty_ids(self) -> None:
        """Test that Builder validates empty ID strings."""
        builder = (
            Position.Builder()
            .with_stock_id("stock-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("100.00")))
        )

        # Empty portfolio_id should raise error
        with pytest.raises(ValueError, match="Portfolio ID must be a non-empty string"):
            _ = builder.with_portfolio_id("").build()

        # Empty stock_id should raise error
        _ = builder.with_portfolio_id("portfolio-1")
        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            _ = builder.with_stock_id("").build()

    def test_builder_method_chaining(self) -> None:
        """Test that all builder methods return self for chaining."""
        builder = Position.Builder()

        assert builder.with_portfolio_id("p1") is builder
        assert builder.with_stock_id("s1") is builder
        assert builder.with_quantity(Quantity(100)) is builder
        assert builder.with_average_cost(Money(Decimal("100.00"))) is builder
        assert builder.with_last_transaction_date(datetime.now(UTC)) is builder
        assert builder.with_id("id1") is builder

    def test_position_constructor_requires_builder(self) -> None:
        """Test that Position constructor requires a builder instance."""
        with pytest.raises(
            ValueError,
            match="Position must be created through Builder",
        ):
            _ = Position(_builder_instance=None)


class TestPosition:
    """Test suite for Position domain entity."""

    def test_create_position_with_value_objects(self) -> None:
        """Should create Position entity with value objects only."""
        portfolio_id = "portfolio-1"
        stock_id = "stock-2"
        quantity = Quantity(100)
        average_cost = Money(Decimal("150.25"))
        last_transaction_date = datetime(2024, 1, 15, tzinfo=UTC)

        position = (
            Position.Builder()
            .with_portfolio_id(portfolio_id)
            .with_stock_id(stock_id)
            .with_quantity(quantity)
            .with_average_cost(average_cost)
            .with_last_transaction_date(last_transaction_date)
            .build()
        )

        assert position.portfolio_id == portfolio_id
        assert position.stock_id == stock_id
        assert position.quantity == quantity
        assert position.average_cost == average_cost
        assert position.last_transaction_date == last_transaction_date
        assert position.id is not None  # Generated UUID
        assert isinstance(position.id, str)

    def test_create_position_with_minimal_data(self) -> None:
        """Should create Position with only required fields."""
        portfolio_id = "portfolio-1"
        stock_id = "stock-2"
        quantity = Quantity(50)
        average_cost = Money(Decimal("175.50"))

        position = (
            Position.Builder()
            .with_portfolio_id(portfolio_id)
            .with_stock_id(stock_id)
            .with_quantity(quantity)
            .with_average_cost(average_cost)
            .build()
        )

        assert position.portfolio_id == portfolio_id
        assert position.stock_id == stock_id
        assert position.quantity == quantity
        assert position.average_cost == average_cost
        assert position.last_transaction_date is None

    def test_position_stores_value_objects(self) -> None:
        """Should store and return value objects directly."""
        quantity = Quantity(75)
        average_cost = Money(Decimal("200.00"))

        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(quantity)
            .with_average_cost(average_cost)
            .build()
        )

        # Should return the exact same value objects
        assert position.quantity is quantity
        assert position.average_cost is average_cost

        # Value access through value property
        assert position.quantity.value == 75
        assert position.average_cost.amount == Decimal("200.00")

    def test_position_equality(self) -> None:
        """Should compare positions based on ID."""
        position1 = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("100.00")))
            .build()
        )

        position2 = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("100.00")))
            .build()
        )

        position3 = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-2")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("100.00")))
            .build()
        )

        # Different instances with same attributes but different IDs are NOT equal
        assert position1 != position2  # Different IDs
        assert position1 != position3  # Different IDs

        # Same ID means equal
        position4 = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("100.00")))
            .with_id("same-id")
            .build()
        )
        position5 = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-2")
            .with_stock_id("stock-id-2")
            .with_quantity(Quantity(200))
            .with_average_cost(Money(Decimal("200.00")))
            .with_id("same-id")
            .build()
        )
        assert position4 == position5  # Same ID, even with different attributes

    def test_position_string_representation(self) -> None:
        """Should have meaningful string representation."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.50")))
            .build()
        )

        expected = "100 shares @ $150.50 avg cost"
        assert str(position) == expected

    def test_position_repr(self) -> None:
        """Should have detailed repr representation."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-2")
            .with_quantity(Quantity(50))
            .with_average_cost(Money(Decimal("200.00")))
            .build()
        )

        expected = (
            "Position(portfolio_id=portfolio-id-1, stock_id=stock-id-2, "
            "quantity=50, average_cost=$200.00)"
        )
        assert repr(position) == expected

    def test_position_create_with_id(self) -> None:
        """Should create position with provided ID."""
        test_id = "position-id-123"
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("100.00")))
            .with_id(test_id)
            .build()
        )

        assert position.id == test_id

    def test_position_id_immutability(self) -> None:
        """Should not be able to change ID after creation."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("100.00")))
            .with_id("test-id-1")
            .build()
        )

        # ID property should not have a setter
        with pytest.raises(AttributeError):
            position.id = "different-id"  # type: ignore[misc]

    def test_position_from_persistence(self) -> None:
        """Should create position from persistence with existing ID."""
        test_id = "persistence-id-456"
        position = (
            Position.Builder()
            .with_id(test_id)
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("100.00")))
            .build()
        )

        assert position.id == test_id
        assert position.portfolio_id == "portfolio-id-1"
        assert position.stock_id == "stock-id-1"


class TestPositionBusinessMethods:
    """Test suite for Position business methods."""

    def test_calculate_total_cost(self) -> None:
        """Should calculate total cost of position."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.50")))
            .build()
        )

        total_cost = position.calculate_total_cost()

        assert total_cost == Money(Decimal("15050.00"))
        assert isinstance(total_cost, Money)

    def test_calculate_current_value(self) -> None:
        """Should calculate current value of position."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.50")))
            .build()
        )

        current_price = Money(Decimal("175.00"))
        current_value = position.calculate_current_value(current_price)

        assert current_value == Money(Decimal("17500.00"))
        assert isinstance(current_value, Money)

    def test_calculate_gain_loss(self) -> None:
        """Should calculate gain/loss of position."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.50")))
            .build()
        )

        # Profitable position
        current_price = Money(Decimal("175.00"))
        gain_loss = position.calculate_gain_loss(current_price)
        assert gain_loss == Money(Decimal("2450.00"))

        # Loss position
        current_price = Money(Decimal("125.00"))
        gain_loss = position.calculate_gain_loss(current_price)
        assert gain_loss == Money(Decimal("-2550.00"))

    def test_calculate_gain_loss_percentage(self) -> None:
        """Should calculate gain/loss percentage of position."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.00")))
            .build()
        )

        # Test 20% gain scenario
        current_price = Money(Decimal("180.00"))
        gain_loss_pct = position.calculate_gain_loss_percentage(current_price)
        assert gain_loss_pct == Decimal("20.00")

        # Test 10% loss scenario
        current_price = Money(Decimal("135.00"))
        gain_loss_pct = position.calculate_gain_loss_percentage(current_price)
        assert gain_loss_pct == Decimal("-10.00")

    def test_calculate_gain_loss_percentage_zero_cost(self) -> None:
        """Should handle zero cost edge case."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("0.00")))
            .build()
        )

        current_price = Money(Decimal("100.00"))
        with pytest.raises(
            ZeroDivisionError,
            match="Cannot calculate percentage with zero cost",
        ):
            _ = position.calculate_gain_loss_percentage(current_price)

    def test_is_profitable(self) -> None:
        """Should check if position is profitable."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.00")))
            .build()
        )

        # Profitable
        assert position.is_profitable(Money(Decimal("175.00"))) is True

        # Not profitable
        assert position.is_profitable(Money(Decimal("125.00"))) is False

        # Break even
        assert position.is_profitable(Money(Decimal("150.00"))) is False

    def test_add_shares(self) -> None:
        """Should add shares and update average cost using weighted average."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.00")))
            .build()
        )

        # Add 50 shares at $200 each
        # Original: 100 shares * $150 = $15,000
        # New: 50 shares * $200 = $10,000
        # Total: 150 shares * $166.67 = $25,000
        position.add_shares(Quantity(50), Money(Decimal("200.00")))

        assert position.quantity.value == 150
        assert position.average_cost.amount == Decimal("166.67")

    def test_add_shares_updates_transaction_date(self) -> None:
        """Should update last transaction date when adding shares."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.00")))
            .build()
        )

        original_date = position.last_transaction_date
        position.add_shares(Quantity(50), Money(Decimal("200.00")))

        assert position.last_transaction_date is not None
        assert position.last_transaction_date != original_date

    def test_remove_shares(self) -> None:
        """Should remove shares while preserving average cost."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.00")))
            .build()
        )

        position.remove_shares(Quantity(25))

        assert position.quantity.value == 75
        assert position.average_cost.amount == Decimal("150.00")  # Unchanged

    def test_remove_shares_updates_transaction_date(self) -> None:
        """Should update last transaction date when removing shares."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.00")))
            .build()
        )

        original_date = position.last_transaction_date
        position.remove_shares(Quantity(25))

        assert position.last_transaction_date is not None
        assert position.last_transaction_date != original_date

    def test_remove_shares_validation(self) -> None:
        """Should validate share removal doesn't exceed quantity."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.00")))
            .build()
        )

        with pytest.raises(
            ValueError,
            match="Cannot remove more shares than currently held",
        ):
            _ = position.remove_shares(Quantity(150))

    def test_remove_all_shares(self) -> None:
        """Should be able to remove all shares."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.00")))
            .build()
        )

        position.remove_shares(Quantity(100))

        assert position.quantity.value == 0
        assert position.average_cost.amount == Decimal("150.00")  # Preserved

    def test_add_zero_shares(self) -> None:
        """Should handle adding zero shares."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.00")))
            .build()
        )

        position.add_shares(Quantity(0), Money(Decimal("200.00")))

        assert position.quantity.value == 100
        assert position.average_cost.amount == Decimal("150.00")

    def test_remove_zero_shares(self) -> None:
        """Should handle removing zero shares."""
        position = (
            Position.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_quantity(Quantity(100))
            .with_average_cost(Money(Decimal("150.00")))
            .build()
        )

        position.remove_shares(Quantity(0))

        assert position.quantity.value == 100
        assert position.average_cost.amount == Decimal("150.00")
