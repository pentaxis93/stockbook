"""
Tests for Target domain entity.

Following TDD approach with focus on value object purity and business logic.
Tests define expected behavior before implementation.
"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from src.domain.entities.target import Target
from src.domain.value_objects import Money, Notes, TargetStatus


class TestTargetBuilder:
    """Test cases for Target.Builder pattern."""

    def test_builder_creates_target_with_all_fields(self) -> None:
        """Test that Builder can create a target with all fields."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_notes(Notes("Important target"))
            .with_id("target-id")
            .build()
        )

        assert target.portfolio_id == "portfolio-1"
        assert target.stock_id == "stock-1"
        assert target.pivot_price.amount == Decimal("100.00")
        assert target.failure_price.amount == Decimal("80.00")
        assert target.status.value == "active"
        assert target.created_date == datetime(2024, 1, 15, tzinfo=UTC)
        assert target.notes.value == "Important target"
        assert target.id == "target-id"

    def test_builder_creates_target_with_minimal_fields(self) -> None:
        """Test that Builder can create a target with only required fields."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime(2024, 1, 15, tzinfo=UTC))
            .build()
        )

        assert target.portfolio_id == "portfolio-1"
        assert target.stock_id == "stock-1"
        assert target.pivot_price.amount == Decimal("100.00")
        assert target.failure_price.amount == Decimal("80.00")
        assert target.status.value == "active"
        assert target.created_date == datetime(2024, 1, 15, tzinfo=UTC)
        assert target.notes.value == ""  # Default

    def test_builder_raises_error_when_required_fields_missing(self) -> None:
        """Test that Builder raises error when required fields are missing."""
        # Missing portfolio_id
        with pytest.raises(ValueError, match="Portfolio ID is required"):
            _ = (
                Target.Builder()
                .with_stock_id("stock-1")
                .with_pivot_price(Money(Decimal("100.00")))
                .with_failure_price(Money(Decimal("80.00")))
                .with_status(TargetStatus("active"))
                .with_created_date(datetime(2024, 1, 15, tzinfo=UTC))
                .build()
            )

        # Missing stock_id
        with pytest.raises(ValueError, match="Stock ID is required"):
            _ = (
                Target.Builder()
                .with_portfolio_id("portfolio-1")
                .with_pivot_price(Money(Decimal("100.00")))
                .with_failure_price(Money(Decimal("80.00")))
                .with_status(TargetStatus("active"))
                .with_created_date(datetime(2024, 1, 15, tzinfo=UTC))
                .build()
            )

        # Missing pivot_price
        with pytest.raises(ValueError, match="Pivot price is required"):
            _ = (
                Target.Builder()
                .with_portfolio_id("portfolio-1")
                .with_stock_id("stock-1")
                .with_failure_price(Money(Decimal("80.00")))
                .with_status(TargetStatus("active"))
                .with_created_date(datetime(2024, 1, 15, tzinfo=UTC))
                .build()
            )

        # Missing failure_price
        with pytest.raises(ValueError, match="Failure price is required"):
            _ = (
                Target.Builder()
                .with_portfolio_id("portfolio-1")
                .with_stock_id("stock-1")
                .with_pivot_price(Money(Decimal("100.00")))
                .with_status(TargetStatus("active"))
                .with_created_date(datetime(2024, 1, 15, tzinfo=UTC))
                .build()
            )

        # Missing status
        with pytest.raises(ValueError, match="Status is required"):
            _ = (
                Target.Builder()
                .with_portfolio_id("portfolio-1")
                .with_stock_id("stock-1")
                .with_pivot_price(Money(Decimal("100.00")))
                .with_failure_price(Money(Decimal("80.00")))
                .with_created_date(datetime(2024, 1, 15, tzinfo=UTC))
                .build()
            )

        # Missing created_date
        with pytest.raises(ValueError, match="Created date is required"):
            _ = (
                Target.Builder()
                .with_portfolio_id("portfolio-1")
                .with_stock_id("stock-1")
                .with_pivot_price(Money(Decimal("100.00")))
                .with_failure_price(Money(Decimal("80.00")))
                .with_status(TargetStatus("active"))
                .build()
            )

    def test_builder_validates_empty_ids(self) -> None:
        """Test that Builder validates empty ID strings."""
        builder = (
            Target.Builder()
            .with_stock_id("stock-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime(2024, 1, 15, tzinfo=UTC))
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
        builder = Target.Builder()

        assert builder.with_portfolio_id("p1") is builder
        assert builder.with_stock_id("s1") is builder
        assert builder.with_pivot_price(Money(Decimal("100.00"))) is builder
        assert builder.with_failure_price(Money(Decimal("80.00"))) is builder
        assert builder.with_status(TargetStatus("active")) is builder
        assert builder.with_created_date(datetime(2024, 1, 15, tzinfo=UTC)) is builder
        assert builder.with_notes(Notes("test")) is builder
        assert builder.with_id("id1") is builder

    def test_target_constructor_requires_builder(self) -> None:
        """Test that Target constructor requires a builder instance."""
        with pytest.raises(ValueError, match="Target must be created through Builder"):
            _ = Target(_builder_instance=None)


class TestTarget:
    """Test Target domain entity with value objects and business logic."""

    def test_create_target_with_value_objects(self) -> None:
        """Test creating a target with all value objects."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_notes(Notes("Important target level"))
            .build()
        )

        assert target.portfolio_id == "portfolio-id-1"
        assert target.stock_id == "stock-id-1"
        assert target.pivot_price.amount == Decimal("100.00")
        assert target.failure_price.amount == Decimal("80.00")
        assert target.status.value == "active"
        assert target.created_date == datetime(2024, 1, 15, tzinfo=UTC)
        assert target.notes.value == "Important target level"

    def test_create_target_with_minimal_data(self) -> None:
        """Test creating target with only required fields."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("150.00")))
            .with_failure_price(Money(Decimal("120.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        assert target.portfolio_id == "portfolio-id-1"
        assert target.stock_id == "stock-id-1"
        assert target.pivot_price.amount == Decimal("150.00")
        assert target.failure_price.amount == Decimal("120.00")
        assert target.status.value == "active"
        assert target.notes.value == ""  # Defaults to empty when not provided

    def test_create_target_with_none_notes_allowed(self) -> None:
        """Should allow creating target with None for notes."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .with_notes(None)
            .build()
        )

        assert target.notes.value == ""  # Notes defaults to empty when None

    def test_create_target_with_invalid_portfolio_id_raises_error(self) -> None:
        """Should raise error for invalid portfolio ID."""
        with pytest.raises(ValueError, match="Portfolio ID must be a non-empty string"):
            _ = (
                Target.Builder()
                .with_portfolio_id("")  # Invalid empty string
                .with_stock_id("stock-id-1")
                .with_pivot_price(Money(Decimal("100.00")))
                .with_failure_price(Money(Decimal("80.00")))
                .with_status(TargetStatus("active"))
                .with_created_date(datetime.now(UTC))
                .build()
            )

    def test_create_target_with_invalid_stock_id_raises_error(self) -> None:
        """Should raise error for invalid stock ID."""
        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            _ = (
                Target.Builder()
                .with_portfolio_id("portfolio-id-1")
                .with_stock_id("")  # Invalid empty string
                .with_pivot_price(Money(Decimal("100.00")))
                .with_failure_price(Money(Decimal("80.00")))
                .with_status(TargetStatus("active"))
                .with_created_date(datetime.now(UTC))
                .build()
            )

    def test_create_target_with_invalid_status_raises_error(self) -> None:
        """Should raise error for invalid target status through TargetStatus value
        object."""
        with pytest.raises(ValueError, match="Target status must be one of"):
            _ = TargetStatus(
                "invalid_status",
            )  # Error happens at TargetStatus construction

    def test_target_equality(self) -> None:
        """Should compare targets based on ID."""
        target1 = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        target2 = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("110.00")))
            .with_failure_price(Money(Decimal("85.00")))
            .with_status(TargetStatus("hit"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        target3 = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-2")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        # Different instances with same attributes but different IDs are NOT equal
        assert target1 != target2  # Different IDs
        assert target1 != target3  # Different IDs

        # Same ID means equal
        target4 = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .with_id("same-id")
            .build()
        )
        target5 = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-2")
            .with_stock_id("stock-id-2")
            .with_pivot_price(Money(Decimal("200.00")))
            .with_failure_price(Money(Decimal("150.00")))
            .with_status(TargetStatus("hit"))
            .with_created_date(datetime(2024, 2, 1, tzinfo=UTC))
            .with_id("same-id")
            .build()
        )
        assert target4 == target5  # Same ID, even with different attributes

    def test_target_hash(self) -> None:
        """Should hash consistently based on ID."""
        target1 = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        target2 = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("150.00")))
            .with_failure_price(Money(Decimal("120.00")))
            .with_status(TargetStatus("hit"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        # Different IDs should have different hashes (likely but not guaranteed)
        assert hash(target1) != hash(target2)  # Different IDs

        # Same ID should have same hash
        target3 = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .with_id("same-id")
            .build()
        )
        target4 = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-2")
            .with_stock_id("stock-id-2")
            .with_pivot_price(Money(Decimal("200.00")))
            .with_failure_price(Money(Decimal("150.00")))
            .with_status(TargetStatus("cancelled"))
            .with_created_date(datetime(2024, 3, 1, tzinfo=UTC))
            .with_id("same-id")
            .build()
        )
        assert hash(target3) == hash(target4)  # Same ID, same hash

    def test_target_string_representation(self) -> None:
        """Should have informative string representation."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        assert "100.00" in str(target)
        assert "80.00" in str(target)
        assert "active" in str(target)

    def test_target_repr(self) -> None:
        """Should have detailed repr representation."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        expected = (
            "Target(portfolio_id=portfolio-id-1, stock_id=stock-id-1, status='active')"
        )
        assert repr(target) == expected

    # Business behavior tests
    def test_target_activate(self) -> None:
        """Should be able to activate target."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("cancelled"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        target.activate()
        assert target.status.value == "active"

    def test_target_mark_as_hit(self) -> None:
        """Should be able to mark target as hit."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        target.mark_as_hit()
        assert target.status.value == "hit"

    def test_target_mark_as_failed(self) -> None:
        """Should be able to mark target as failed."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        target.mark_as_failed()
        assert target.status.value == "failed"

    def test_target_cancel(self) -> None:
        """Should be able to cancel target."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        target.cancel()
        assert target.status.value == "cancelled"

    def test_target_is_active(self) -> None:
        """Should check if target is active."""
        active_target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        hit_target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("hit"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        assert active_target.is_active() is True
        assert hit_target.is_active() is False

    def test_target_is_hit(self) -> None:
        """Should check if target is hit."""
        hit_target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("hit"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        active_target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        assert hit_target.is_hit() is True
        assert active_target.is_hit() is False

    def test_target_has_notes(self) -> None:
        """Should check if target has notes."""
        target_with_notes = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .with_notes(Notes("Important target"))
            .build()
        )

        target_without_notes = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        assert target_with_notes.has_notes() is True
        assert target_without_notes.has_notes() is False

    def test_target_update_notes(self) -> None:
        """Should be able to update target notes."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        # Update with Notes value object
        target.update_notes(Notes("Updated notes"))
        assert target.notes.value == "Updated notes"

        # Update with string (should be converted to Notes)
        target.update_notes("String notes")
        assert target.notes.value == "String notes"

    def test_target_create_with_id(self) -> None:
        """Should create target with provided ID."""
        test_id = "target-id-123"
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .with_id(test_id)
            .build()
        )

        assert target.id == test_id

    def test_target_id_immutability(self) -> None:
        """Should not be able to change ID after creation."""
        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .with_id("test-id-1")
            .build()
        )

        # ID property should not have a setter
        with pytest.raises(AttributeError):
            target.id = "different-id"  # type: ignore[misc]

    def test_target_from_persistence(self) -> None:
        """Should create target from persistence with existing ID."""
        test_id = "persistence-id-456"
        target = (
            Target.Builder()
            .with_id(test_id)
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_pivot_price(Money(Decimal("100.00")))
            .with_failure_price(Money(Decimal("80.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime.now(UTC))
            .build()
        )

        assert target.id == test_id
        assert target.portfolio_id == "portfolio-id-1"
        assert target.stock_id == "stock-id-1"


class TestTargetStatus:
    """Test TargetStatus value object validation."""

    def test_valid_target_statuses_accepted(self) -> None:
        """Test that valid target statuses are accepted."""
        valid_statuses = ["active", "hit", "failed", "cancelled"]
        for status in valid_statuses:
            target_status = TargetStatus(status)
            assert target_status.value == status

    def test_target_status_case_insensitive(self) -> None:
        """Test that target statuses are case insensitive."""
        status1 = TargetStatus("ACTIVE")
        status2 = TargetStatus("Active")
        status3 = TargetStatus("active")

        assert status1.value == "active"
        assert status2.value == "active"
        assert status3.value == "active"

    def test_invalid_target_statuses_rejected(self) -> None:
        """Test that invalid target statuses are rejected."""
        invalid_statuses = ["pending", "unknown", "", "INVALID"]
        for status in invalid_statuses:
            with pytest.raises(ValueError, match="Target status must be one of"):
                _ = TargetStatus(status)

    def test_target_status_checks_failed_and_cancelled(self) -> None:
        """Test that target status property methods work correctly."""

        # Test failed status (covers line 115)
        failed_target = (
            Target.Builder()
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-1")
            .with_failure_price(Money(Decimal("90.00")))
            .with_pivot_price(Money(Decimal("110.00")))
            .with_status(TargetStatus("failed"))
            .with_created_date(datetime(2024, 1, 15, tzinfo=UTC))
            .build()
        )
        assert failed_target.is_failed()
        assert not failed_target.is_cancelled()

        # Test cancelled status (covers line 119)
        cancelled_target = (
            Target.Builder()
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-2")
            .with_failure_price(Money(Decimal("90.00")))
            .with_pivot_price(Money(Decimal("110.00")))
            .with_status(TargetStatus("cancelled"))
            .with_created_date(datetime(2024, 1, 15, tzinfo=UTC))
            .build()
        )
        assert cancelled_target.is_cancelled()
        assert not cancelled_target.is_failed()

    def test_target_equality_with_non_target_object(self) -> None:
        """Test that target equality returns False for non-Target objects."""

        target = (
            Target.Builder()
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-1")
            .with_failure_price(Money(Decimal("90.00")))
            .with_pivot_price(Money(Decimal("110.00")))
            .with_status(TargetStatus("active"))
            .with_created_date(datetime(2024, 1, 15, tzinfo=UTC))
            .build()
        )

        # Test equality with different types - should return False (covers line 136)
        assert target != "not a target"
        assert target != 123
        assert target is not None
        assert target != {"portfolio_id": "portfolio-1", "stock_id": "stock-1"}
