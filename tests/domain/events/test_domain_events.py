"""
Tests for domain events.

Following TDD approach - these tests define the expected behavior
of domain events used for inter-aggregate communication.
"""

from datetime import datetime, timezone

import pytest

from src.domain.events.base import DomainEvent
from src.domain.events.stock_events import StockAddedEvent
from src.domain.value_objects.stock_symbol import StockSymbol


class TestDomainEvent:
    """Test suite for base DomainEvent."""

    def test_domain_event_has_timestamp(self) -> None:
        """Should automatically set timestamp when created."""
        event = DomainEvent()

        assert event.occurred_at is not None
        assert isinstance(event.occurred_at, datetime)

        # Should be recent (within last second)
        now = datetime.now(timezone.utc)
        assert (now - event.occurred_at).total_seconds() < 1

    def test_domain_event_with_custom_timestamp(self) -> None:
        """Should allow setting custom timestamp."""
        custom_time = datetime(2024, 1, 15, 10, 30, 0)
        event = DomainEvent(occurred_at=custom_time)

        assert event.occurred_at == custom_time

    def test_domain_event_has_event_id(self) -> None:
        """Should have unique event ID."""
        event1 = DomainEvent()
        event2 = DomainEvent()

        assert event1.event_id is not None
        assert event2.event_id is not None
        assert event1.event_id != event2.event_id

    def test_domain_event_equality(self) -> None:
        """Should compare events by event_id."""
        event1 = DomainEvent()
        event2 = DomainEvent()

        # Same event should equal itself
        assert event1 == event1

        # Different events should not be equal
        assert event1 != event2

    def test_domain_event_hash(self) -> None:
        """Should be hashable by event_id."""
        event1 = DomainEvent()
        event2 = DomainEvent()

        # Can be used in set
        event_set = {event1, event2}
        assert len(event_set) == 2

    def test_domain_event_string_representation(self) -> None:
        """Should have meaningful string representation."""
        event = DomainEvent()
        str_repr = str(event)

        assert "DomainEvent" in str_repr
        assert str(event.event_id) in str_repr


class TestStockAddedEvent:
    """Test suite for StockAddedEvent."""

    def test_create_stock_added_event(self) -> None:
        """Should create StockAddedEvent with stock information."""
        symbol = StockSymbol("AAPL")
        event = StockAddedEvent(
            stock_symbol=symbol, stock_name="Apple Inc.", stock_id=123
        )

        assert event.stock_symbol == symbol
        assert event.stock_name == "Apple Inc."
        assert event.stock_id == 123
        assert event.occurred_at is not None
        assert event.event_id is not None

    def test_stock_added_event_validation(self) -> None:
        """Should validate required fields."""
        symbol = StockSymbol("AAPL")

        with pytest.raises(ValueError, match="Stock name cannot be empty"):
            _ = StockAddedEvent(stock_symbol=symbol, stock_name="", stock_id=123)

        with pytest.raises(ValueError, match="Stock ID must be positive"):
            _ = StockAddedEvent(
                stock_symbol=symbol, stock_name="Apple Inc.", stock_id=0
            )

    def test_stock_added_event_string_representation(self) -> None:
        """Should have meaningful string representation."""
        symbol = StockSymbol("AAPL")
        event = StockAddedEvent(
            stock_symbol=symbol, stock_name="Apple Inc.", stock_id=123
        )

        str_repr = str(event)
        assert "StockAddedEvent" in str_repr
        assert "AAPL" in str_repr
        assert "Apple Inc." in str_repr

    def test_stock_added_event_repr(self) -> None:
        """Should have detailed repr representation."""
        symbol = StockSymbol("AAPL")
        event = StockAddedEvent(
            stock_symbol=symbol, stock_name="Apple Inc.", stock_id=123
        )

        repr_str = repr(event)
        assert "StockAddedEvent" in repr_str
        assert "stock_symbol=StockSymbol('AAPL')" in repr_str
        assert "stock_name='Apple Inc.'" in repr_str
        assert "stock_id=123" in repr_str
