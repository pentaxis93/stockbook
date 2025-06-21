"""
Tests for TargetEntity domain entity.

Following TDD approach with focus on value object purity and business logic.
Tests define expected behavior before implementation.
"""

from datetime import date
from decimal import Decimal

import pytest

from src.domain.entities.target_entity import TargetEntity
from src.domain.value_objects import Money, Notes


class TestTargetEntity:
    """Test TargetEntity domain entity with value objects and business logic."""

    def test_create_target_with_value_objects(self):
        """Test creating a target with all value objects."""
        from src.domain.value_objects import TargetStatus

        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 15),
            notes=Notes("Important target level"),
        )

        assert target.portfolio_id == "portfolio-id-1"
        assert target.stock_id == "stock-id-1"
        assert target.pivot_price.amount == Decimal("100.00")
        assert target.failure_price.amount == Decimal("80.00")
        assert target.status.value == "active"
        assert target.created_date == date(2024, 1, 15)
        assert target.notes.value == "Important target level"

    def test_create_target_with_minimal_data(self):
        """Test creating target with only required fields."""
        from src.domain.value_objects import TargetStatus

        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("150.00")),
            failure_price=Money(Decimal("120.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        assert target.portfolio_id == "portfolio-id-1"
        assert target.stock_id == "stock-id-1"
        assert target.pivot_price.amount == Decimal("150.00")
        assert target.failure_price.amount == Decimal("120.00")
        assert target.status.value == "active"
        assert target.notes.value == ""  # Defaults to empty when not provided

    def test_create_target_with_none_notes_allowed(self):
        """Should allow creating target with None for notes."""
        from src.domain.value_objects import TargetStatus

        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
            notes=None,
        )

        assert target.notes.value == ""  # Notes defaults to empty when None

    def test_create_target_with_invalid_portfolio_id_raises_error(self):
        """Should raise error for invalid portfolio ID."""
        from src.domain.value_objects import TargetStatus

        with pytest.raises(ValueError, match="Portfolio ID must be a non-empty string"):
            TargetEntity(
                portfolio_id="",  # Invalid empty string
                stock_id="stock-id-1",
                pivot_price=Money(Decimal("100.00")),
                failure_price=Money(Decimal("80.00")),
                status=TargetStatus("active"),
                created_date=date.today(),
            )

    def test_create_target_with_invalid_stock_id_raises_error(self):
        """Should raise error for invalid stock ID."""
        from src.domain.value_objects import TargetStatus

        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            TargetEntity(
                portfolio_id="portfolio-id-1",
                stock_id="",  # Invalid empty string
                pivot_price=Money(Decimal("100.00")),
                failure_price=Money(Decimal("80.00")),
                status=TargetStatus("active"),
                created_date=date.today(),
            )

    def test_create_target_with_invalid_status_raises_error(self):
        """Should raise error for invalid target status through TargetStatus value object."""
        from src.domain.value_objects import TargetStatus

        with pytest.raises(ValueError, match="Target status must be one of"):
            TargetStatus("invalid_status")  # Error happens at TargetStatus construction

    def test_target_equality(self):
        """Should compare targets based on business identity (portfolio_id, stock_id)."""
        from src.domain.value_objects import TargetStatus

        target1 = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        target2 = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("110.00")),  # Different price
            failure_price=Money(Decimal("85.00")),
            status=TargetStatus("hit"),  # Different status
            created_date=date.today(),
        )

        target3 = TargetEntity(
            portfolio_id="portfolio-id-2",  # Different portfolio
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        assert target1 == target2  # Same portfolio and stock
        assert target1 != target3  # Different portfolio

    def test_target_hash(self):
        """Should hash consistently based on business identity."""
        from src.domain.value_objects import TargetStatus

        target1 = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        target2 = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("150.00")),  # Different price
            failure_price=Money(Decimal("90.00")),
            status=TargetStatus("hit"),
            created_date=date.today(),
        )

        assert hash(target1) == hash(target2)  # Same portfolio and stock

    def test_target_string_representation(self):
        """Should have informative string representation."""
        from src.domain.value_objects import TargetStatus

        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        assert "100.00" in str(target)
        assert "80.00" in str(target)
        assert "active" in str(target)

    def test_target_repr(self):
        """Should have detailed repr representation."""
        from src.domain.value_objects import TargetStatus

        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        expected = "TargetEntity(portfolio_id=portfolio-id-1, stock_id=stock-id-1, status='active')"
        assert repr(target) == expected

    # Business behavior tests
    def test_target_activate(self):
        """Should be able to activate target."""
        from src.domain.value_objects import TargetStatus

        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("cancelled"),
            created_date=date.today(),
        )

        target.activate()
        assert target.status.value == "active"

    def test_target_mark_as_hit(self):
        """Should be able to mark target as hit."""
        from src.domain.value_objects import TargetStatus

        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        target.mark_as_hit()
        assert target.status.value == "hit"

    def test_target_mark_as_failed(self):
        """Should be able to mark target as failed."""
        from src.domain.value_objects import TargetStatus

        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        target.mark_as_failed()
        assert target.status.value == "failed"

    def test_target_cancel(self):
        """Should be able to cancel target."""
        from src.domain.value_objects import TargetStatus

        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        target.cancel()
        assert target.status.value == "cancelled"

    def test_target_is_active(self):
        """Should check if target is active."""
        from src.domain.value_objects import TargetStatus

        active_target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        hit_target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("hit"),
            created_date=date.today(),
        )

        assert active_target.is_active() is True
        assert hit_target.is_active() is False

    def test_target_is_hit(self):
        """Should check if target is hit."""
        from src.domain.value_objects import TargetStatus

        hit_target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("hit"),
            created_date=date.today(),
        )

        active_target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        assert hit_target.is_hit() is True
        assert active_target.is_hit() is False

    def test_target_has_notes(self):
        """Should check if target has notes."""
        from src.domain.value_objects import TargetStatus

        target_with_notes = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
            notes=Notes("Important target"),
        )

        target_without_notes = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        assert target_with_notes.has_notes() is True
        assert target_without_notes.has_notes() is False

    def test_target_update_notes(self):
        """Should be able to update target notes."""
        from src.domain.value_objects import TargetStatus

        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        # Update with Notes value object
        target.update_notes(Notes("Updated notes"))
        assert target.notes.value == "Updated notes"

        # Update with string (should be converted to Notes)
        target.update_notes("String notes")
        assert target.notes.value == "String notes"

    def test_target_create_with_id(self):
        """Should create target with provided ID."""
        from src.domain.value_objects import TargetStatus

        test_id = "target-id-123"
        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
            entity_id=test_id,
        )

        assert target.id == test_id

    def test_target_id_immutability(self):
        """Should not be able to change ID after creation."""
        from src.domain.value_objects import TargetStatus

        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
            entity_id="test-id-1",
        )

        # ID property should not have a setter
        with pytest.raises(AttributeError):
            target.id = "different-id"

    def test_target_from_persistence(self):
        """Should create target from persistence with existing ID."""
        from src.domain.value_objects import TargetStatus

        test_id = "persistence-id-456"
        target = TargetEntity.from_persistence(
            test_id,
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("80.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )

        assert target.id == test_id
        assert target.portfolio_id == "portfolio-id-1"
        assert target.stock_id == "stock-id-1"


class TestTargetStatus:
    """Test TargetStatus value object validation."""

    def test_valid_target_statuses_accepted(self):
        """Test that valid target statuses are accepted."""
        from src.domain.value_objects import TargetStatus

        valid_statuses = ["active", "hit", "failed", "cancelled"]
        for status in valid_statuses:
            target_status = TargetStatus(status)
            assert target_status.value == status

    def test_target_status_case_insensitive(self):
        """Test that target statuses are case insensitive."""
        from src.domain.value_objects import TargetStatus

        status1 = TargetStatus("ACTIVE")
        status2 = TargetStatus("Active")
        status3 = TargetStatus("active")

        assert status1.value == "active"
        assert status2.value == "active"
        assert status3.value == "active"

    def test_invalid_target_statuses_rejected(self):
        """Test that invalid target statuses are rejected."""
        from src.domain.value_objects import TargetStatus

        invalid_statuses = ["pending", "unknown", "", "INVALID"]
        for status in invalid_statuses:
            with pytest.raises(ValueError):
                TargetStatus(status)
