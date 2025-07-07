"""
Tests for domain events.

Following TDD approach - these tests define the expected behavior
of domain events used for inter-aggregate communication.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

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
        now = datetime.now(UTC)
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
        assert event1 == event1  # pylint: disable=comparison-with-itself

        # Different events should not be equal
        assert event1 != event2

        # Event should not equal non-DomainEvent objects
        assert event1 != "not an event"
        assert event1 != 42
        assert event1 is not None
        assert event1

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

    def test_domain_event_repr_representation(self) -> None:
        """Should have meaningful repr representation."""
        event = DomainEvent()
        repr_str = repr(event)

        assert "DomainEvent" in repr_str
        assert event.event_id in repr_str
        assert event.occurred_at.isoformat() in repr_str


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


class TestDomainEventLifecycle:
    """Test domain event lifecycle and handling patterns."""

    def test_event_creation_and_metadata(self) -> None:
        """Should create events with proper metadata."""
        # Create a stock added event
        stock_symbol = StockSymbol("AAPL")
        stock_name = "Apple Inc."
        stock_id = 1
        event = StockAddedEvent(
            stock_symbol=stock_symbol, stock_name=stock_name, stock_id=stock_id
        )

        # Verify event metadata
        assert event.event_id is not None
        assert event.occurred_at is not None
        assert isinstance(event.occurred_at, datetime)
        assert event.stock_symbol == stock_symbol
        assert event.stock_name == stock_name
        assert event.stock_id == stock_id

        # Event should be recent
        now = datetime.now(UTC)
        assert (now - event.occurred_at).total_seconds() < 1

    def test_event_immutability(self) -> None:
        """Should ensure events are immutable after creation."""
        event = StockAddedEvent(
            stock_symbol=StockSymbol("TEST"), stock_name="Test Company", stock_id=1
        )

        # Should not be able to modify event after creation
        with pytest.raises(AttributeError):
            event.event_id = "different-id"  # type: ignore[misc]

        with pytest.raises(AttributeError):
            event.occurred_at = datetime.now()  # type: ignore[misc]

    def test_event_ordering_by_timestamp(self) -> None:
        """Should support chronological ordering of events."""
        # Create events with specific timestamps
        early_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)
        later_time = datetime(2024, 1, 1, 11, 0, 0, tzinfo=UTC)

        early_event = StockAddedEvent(
            stock_symbol=StockSymbol("AAPL"),
            stock_name="Apple Inc.",
            stock_id=1,
            occurred_at=early_time,
        )

        later_event = StockAddedEvent(
            stock_symbol=StockSymbol("MSFT"),
            stock_name="Microsoft Corp",
            stock_id=2,
            occurred_at=later_time,
        )

        # Events should be orderable by timestamp
        events = [later_event, early_event]
        sorted_events = sorted(events, key=lambda e: e.occurred_at)

        assert sorted_events[0] == early_event
        assert sorted_events[1] == later_event

    def test_event_serialization_properties(self) -> None:
        """Should have properties suitable for serialization."""
        event = StockAddedEvent(
            stock_symbol=StockSymbol("GOOGL"), stock_name="Alphabet Inc.", stock_id=1
        )

        # Event should have string representation
        str_repr = str(event)
        assert "StockAddedEvent" in str_repr
        assert "GOOGL" in str_repr

        # Event should have meaningful repr
        repr_str = repr(event)
        assert "StockAddedEvent" in repr_str
        assert "StockAddedEvent" in repr_str


class TestDomainEventConsistency:
    """Test domain event consistency and integrity."""

    def test_event_data_consistency(self) -> None:
        """Should maintain data consistency throughout event lifecycle."""
        stock_symbol = StockSymbol("TSLA")

        event = StockAddedEvent(
            stock_symbol=stock_symbol, stock_name="Tesla Inc.", stock_id=1
        )

        # Event data should remain consistent
        assert event.stock_symbol.value == "TSLA"
        assert event.stock_name == "Tesla Inc."

        # Value objects should maintain integrity
        assert event.stock_symbol == stock_symbol

    def test_event_uniqueness_guarantees(self) -> None:
        """Should guarantee event uniqueness through event IDs."""
        events: list[StockAddedEvent] = []

        # Create multiple events
        for _ in range(100):
            event = StockAddedEvent(
                stock_symbol=StockSymbol("TEST"), stock_name="Test Company", stock_id=1
            )
            events.append(event)

        # All event IDs should be unique
        event_ids = {event.event_id for event in events}
        assert len(event_ids) == 100

        # Events should be unique in collections
        event_set = set(events)
        assert len(event_set) == 100

    def test_event_temporal_consistency(self) -> None:
        """Should maintain temporal consistency across events."""
        events: list[StockAddedEvent] = []

        # Create events in sequence
        for i in range(10):
            event = StockAddedEvent(
                stock_symbol=StockSymbol("TEST"), stock_name="Test Company", stock_id=1
            )
            events.append(event)

            # Small delay to ensure timestamp progression
            import time

            time.sleep(0.001)

        # Events should have non-decreasing timestamps
        for i in range(1, len(events)):
            assert events[i].occurred_at >= events[i - 1].occurred_at


class TestDomainEventPatterns:
    """Test domain event patterns and integration scenarios."""

    def test_event_collection_operations(self) -> None:
        """Should work properly in event collections."""
        events: list[StockAddedEvent] = []

        # Create diverse events
        events.append(
            StockAddedEvent(
                stock_symbol=StockSymbol("TEST"), stock_name="Test Company", stock_id=1
            )
        )

        events.append(
            StockAddedEvent(
                stock_symbol=StockSymbol("TEST"), stock_name="Test Company", stock_id=1
            )
        )

        # Events should work in lists
        assert len(events) == 2

        # Events should work in sets (based on event_id)
        event_set = set(events)
        assert len(event_set) == 2

        # Events should work as dictionary keys
        event_metadata = {
            events[0]: {"processed": True, "handler": "stock_handler"},
            events[1]: {"processed": False, "handler": "stock_handler"},
        }
        assert len(event_metadata) == 2

    def test_event_filtering_and_querying(self) -> None:
        """Should support event filtering and querying patterns."""
        events: list[StockAddedEvent] = []

        # Create mixed events
        for i in range(20):
            # Use alphabet letters for valid symbols
            symbol = chr(ord("A") + (i % 26)) + chr(ord("A") + ((i // 26) % 26))
            company_name = f"Tech Company {i}" if i % 2 == 0 else f"Finance Company {i}"

            event = StockAddedEvent(
                stock_symbol=StockSymbol(symbol),
                stock_name=company_name,
                stock_id=i + 1,
            )
            events.append(event)

        # Filter by company name pattern
        tech_events = [e for e in events if "Tech" in e.stock_name]
        finance_events = [e for e in events if "Finance" in e.stock_name]

        assert len(tech_events) == 10
        assert len(finance_events) == 10

        # Filter by symbol pattern (first letter)
        a_through_m_events = [e for e in events if e.stock_symbol.value[0] <= "M"]
        assert len(a_through_m_events) == 13  # A through M is 13 letters

    def test_event_aggregation_patterns(self) -> None:
        """Should support event aggregation and summary patterns."""
        events: list[StockAddedEvent] = []

        # Create events with timestamps over a time range (span multiple hours)
        base_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)

        for i in range(50):
            # Create events across multiple hours (every 5 minutes = 12 events per hour)
            event_time = base_time + timedelta(minutes=i * 5)
            event = StockAddedEvent(
                stock_symbol=StockSymbol(
                    chr(ord("A") + (i % 26)) + chr(ord("A") + ((i // 26) % 26))
                ),
                stock_name=f"Aggregated Company {i}",
                stock_id=i + 1,
                occurred_at=event_time,
            )
            events.append(event)

        # Group events by hour
        events_by_hour: dict[int, list[StockAddedEvent]] = {}
        for event in events:
            hour_key = event.occurred_at.hour
            if hour_key not in events_by_hour:
                events_by_hour[hour_key] = []
            events_by_hour[hour_key].append(event)

        # Should have events distributed across hours
        assert len(events_by_hour) > 1
        assert (
            sum(len(hourly_events) for hourly_events in events_by_hour.values()) == 50
        )

    def test_event_handler_simulation(self) -> None:
        """Should simulate event handler processing patterns."""
        events: list[StockAddedEvent] = []
        processed_events: list[StockAddedEvent] = []
        failed_events: list[StockAddedEvent] = []

        # Create test events with different symbols
        for i in range(10):
            symbol = f"SYM{i:02d}"[
                :5
            ]  # Ensure 5 chars max and no digits in stock symbol
            # Use letters only for stock symbols
            if i == 5:
                symbol = "FAILS"  # This will trigger the failure condition
            else:
                symbol = f"{chr(ord('A') + i)}{chr(ord('A') + (i % 26))}"
            event = StockAddedEvent(
                stock_symbol=StockSymbol(symbol),
                stock_name="Test Company",
                stock_id=i + 1,
            )
            events.append(event)

        # Simulate event processing
        for event in events:
            try:
                # Simulate processing logic
                if "FAILS" in event.stock_symbol.value:
                    # Simulate processing failure
                    raise ValueError(
                        f"Processing failed for {event.stock_symbol.value}"
                    )

                # Successful processing
                processed_events.append(event)

            except ValueError:
                # Failed processing
                failed_events.append(event)

        # Verify processing results
        assert len(processed_events) == 9  # All except FAILS
        assert len(failed_events) == 1  # Only FAILS
        assert processed_events[0].stock_symbol.value == "AA"
        assert failed_events[0].stock_symbol.value == "FAILS"


class TestDomainEventEdgeCases:
    """Test edge cases and boundary conditions for domain events."""

    def test_event_with_boundary_timestamps(self) -> None:
        """Should handle boundary timestamp conditions."""
        # Test with very early timestamp
        early_event = StockAddedEvent(
            stock_symbol=StockSymbol("EARLY"),
            stock_name="Early Company",
            stock_id=1,
            occurred_at=datetime.min.replace(tzinfo=UTC),
        )

        # Test with far future timestamp
        future_event = StockAddedEvent(
            stock_symbol=StockSymbol("FUTUR"),
            stock_name="Future Company",
            stock_id=2,
            occurred_at=datetime(2050, 12, 31, 23, 59, 59, tzinfo=UTC),
        )

        assert early_event.occurred_at.year == datetime.min.year
        assert future_event.occurred_at.year == 2050

    def test_event_with_extreme_data_values(self) -> None:
        """Should handle extreme data values in events."""
        # Test with minimal symbol
        minimal_event = StockAddedEvent(
            stock_symbol=StockSymbol("A"), stock_name="Test Company", stock_id=1
        )

        # Test with maximal symbol (at symbol length limit of 5)
        maximal_symbol = "AAAAA"  # Max symbol length is 5
        maximal_name = "A" * 200  # Long company name

        maximal_event = StockAddedEvent(
            stock_symbol=StockSymbol(maximal_symbol),
            stock_name=maximal_name,
            stock_id=2,
        )

        assert minimal_event.stock_symbol.value == "A"
        assert maximal_event.stock_symbol.value == maximal_symbol
        assert len(maximal_event.stock_name) == 200

    def test_event_memory_efficiency(self) -> None:
        """Should maintain memory efficiency with large event volumes."""
        events: list[StockAddedEvent] = []

        # Create large number of events
        for i in range(1000):
            # Generate valid symbols using letters only
            symbol = (
                f"{chr(ord('A') + (i % 26))}"
                f"{chr(ord('A') + ((i // 26) % 26))}"
                f"{chr(ord('A') + ((i // 676) % 26))}"
            )
            event = StockAddedEvent(
                stock_symbol=StockSymbol(symbol),
                stock_name=f"Company {i}",
                stock_id=i + 1,
            )
            events.append(event)

        # Verify all events are created and accessible
        assert len(events) == 1000
        assert events[0].stock_symbol.value == "AAA"
        # Just verify we have the right number of events with valid symbols
        assert all(len(event.stock_symbol.value) <= 5 for event in events)

        # Events should maintain unique identities
        unique_ids = {event.event_id for event in events}
        assert len(unique_ids) == 1000

    def test_event_concurrent_creation_simulation(self) -> None:
        """Should handle concurrent-like event creation patterns."""
        events_batch_1: list[StockAddedEvent] = []
        events_batch_2: list[StockAddedEvent] = []

        # Simulate concurrent batches of event creation
        for i in range(50):
            # Batch 1 events - use different symbols (only letters)
            symbol1 = f"BA{chr(ord('A') + (i % 26))}"
            event1 = StockAddedEvent(
                stock_symbol=StockSymbol(symbol1),
                stock_name="Batch 1 Company",
                stock_id=i + 1,
            )
            events_batch_1.append(event1)

            # Batch 2 events - use different symbols (only letters)
            symbol2 = f"BB{chr(ord('A') + (i % 26))}"
            event2 = StockAddedEvent(
                stock_symbol=StockSymbol(symbol2),
                stock_name="Batch 2 Company",
                stock_id=i + 51,
            )
            events_batch_2.append(event2)

        # All events should have unique IDs despite concurrent creation
        all_events = events_batch_1 + events_batch_2
        unique_ids = {event.event_id for event in all_events}
        assert len(unique_ids) == 100

        # Events should be distinguishable
        batch1_symbols = {event.stock_symbol.value for event in events_batch_1}
        batch2_symbols = {event.stock_symbol.value for event in events_batch_2}
        assert len(batch1_symbols.intersection(batch2_symbols)) == 0  # No overlap


class TestDomainEventArchitecturalConcerns:
    """Test architectural concerns and design patterns for domain events."""

    def test_event_base_class_contract(self) -> None:
        """Should verify base event class provides proper contract."""
        # All events should inherit from DomainEvent
        stock_event = StockAddedEvent(
            stock_symbol=StockSymbol("TEST"), stock_name="Test Company", stock_id=1
        )

        assert isinstance(stock_event, DomainEvent)

        # Should have all required base event properties
        assert hasattr(stock_event, "event_id")
        assert hasattr(stock_event, "occurred_at")

        # Should support base event operations
        assert stock_event == stock_event  # pylint: disable=comparison-with-itself
        assert hash(stock_event) is not None  # Hashability
        assert str(stock_event) is not None  # String representation

    def test_event_polymorphism_support(self) -> None:
        """Should support polymorphic event handling."""
        events: list[DomainEvent] = []

        # Add different types of events to same collection
        stock_event = StockAddedEvent(
            stock_symbol=StockSymbol("TEST"), stock_name="Test Company", stock_id=1
        )
        events.append(stock_event)

        # Add base domain event
        base_event = DomainEvent()
        events.append(base_event)

        # Should be able to process polymorphically
        for event in events:
            assert hasattr(event, "event_id")
            assert hasattr(event, "occurred_at")
            assert isinstance(event, DomainEvent)

        # Should be able to filter by type
        stock_events = [e for e in events if isinstance(e, StockAddedEvent)]
        assert len(stock_events) == 1

    def test_event_extensibility_patterns(self) -> None:
        """Should support event extensibility for future enhancements."""
        event = StockAddedEvent(
            stock_symbol=StockSymbol("TEST"), stock_name="Test Company", stock_id=1
        )

        # Event should support metadata attachment (conceptually)
        # This tests the design's extensibility for adding metadata
        event_data: dict[str, Any] = {
            "event": event,
            "metadata": {
                "source": "user_input",
                "correlation_id": "test-correlation-123",
                "version": "1.0",
            },
        }

        assert event_data["event"] == event
        assert event_data["metadata"]["source"] == "user_input"

        # Should support event wrapper patterns
        class EventWrapper:
            def __init__(self, event: DomainEvent, context: dict[str, Any]) -> None:
                self.event = event
                self.context = context

        wrapped_event = EventWrapper(event, {"handler": "stock_service"})
        assert wrapped_event.event == event
        assert wrapped_event.context["handler"] == "stock_service"
