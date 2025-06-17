"""
Comprehensive test suite for base domain events in shared kernel.

Tests the foundational event infrastructure as a reusable component 
across all bounded contexts. This follows TDD approach by defining 
all expected behavior before implementation.
"""

import pytest
from datetime import datetime, timedelta
from uuid import UUID
from shared_kernel.events.base import DomainEvent


class TestDomainEventCreation:
    """Test base DomainEvent creation and initialization."""
    
    def test_create_domain_event_with_defaults(self):
        """Should create domain event with auto-generated timestamp and ID."""
        event = DomainEvent()
        
        # Should have timestamp close to now
        assert isinstance(event.timestamp, datetime)
        time_diff = abs((datetime.now() - event.timestamp).total_seconds())
        assert time_diff < 1  # Within 1 second
        
        # Should have unique event ID
        assert isinstance(event.event_id, str)
        assert len(event.event_id) > 0
    
    def test_create_domain_event_with_custom_timestamp(self):
        """Should create domain event with custom timestamp."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        event = DomainEvent(timestamp=custom_time)
        
        assert event.timestamp == custom_time
    
    def test_create_domain_event_with_custom_event_id(self):
        """Should create domain event with custom event ID."""
        custom_id = "custom-event-123"
        event = DomainEvent(event_id=custom_id)
        
        assert event.event_id == custom_id
    
    def test_auto_generated_event_ids_are_unique(self):
        """Should generate unique event IDs for each event."""
        event1 = DomainEvent()
        event2 = DomainEvent()
        
        assert event1.event_id != event2.event_id
    
    def test_event_id_is_uuid_format(self):
        """Should generate event IDs in UUID format by default."""
        event = DomainEvent()
        
        # Should be parseable as UUID
        uuid_obj = UUID(event.event_id)
        assert str(uuid_obj) == event.event_id


class TestDomainEventEquality:
    """Test DomainEvent equality and identity."""
    
    def test_events_equal_with_same_id(self):
        """Should be equal when having same event ID."""
        event_id = "test-event-123"
        event1 = DomainEvent(event_id=event_id)
        event2 = DomainEvent(event_id=event_id)
        
        assert event1 == event2
    
    def test_events_not_equal_with_different_ids(self):
        """Should not be equal when having different event IDs."""
        event1 = DomainEvent(event_id="event-1")
        event2 = DomainEvent(event_id="event-2")
        
        assert event1 != event2
    
    def test_events_not_equal_with_different_types(self):
        """Should not be equal when compared to different types."""
        event = DomainEvent()
        
        assert event != "not an event"
        assert event != 123
        assert event != None
    
    def test_event_hash_consistency(self):
        """Should have consistent hash based on event ID."""
        event_id = "test-event-123"
        event1 = DomainEvent(event_id=event_id)
        event2 = DomainEvent(event_id=event_id)
        
        assert hash(event1) == hash(event2)
        
        # Should be usable in sets and as dict keys
        event_set = {event1, event2}
        assert len(event_set) == 1
        
        event_dict = {event1: "first", event2: "second"}
        assert len(event_dict) == 1


class TestDomainEventSerialization:
    """Test DomainEvent serialization and deserialization."""
    
    def test_to_dict_representation(self):
        """Should serialize to dictionary representation."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        event_id = "test-event-123"
        event = DomainEvent(timestamp=timestamp, event_id=event_id)
        
        event_dict = event.to_dict()
        
        assert event_dict["event_id"] == event_id
        assert event_dict["timestamp"] == timestamp.isoformat()
        assert event_dict["event_type"] == "DomainEvent"
    
    def test_from_dict_deserialization(self):
        """Should deserialize from dictionary representation."""
        event_dict = {
            "event_id": "test-event-123",
            "timestamp": "2023-01-01T12:00:00",
            "event_type": "DomainEvent"
        }
        
        event = DomainEvent.from_dict(event_dict)
        
        assert event.event_id == "test-event-123"
        assert event.timestamp == datetime(2023, 1, 1, 12, 0, 0)
    
    def test_round_trip_serialization(self):
        """Should maintain consistency through serialize/deserialize cycle."""
        original_event = DomainEvent(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            event_id="test-event-123"
        )
        
        # Serialize and deserialize
        event_dict = original_event.to_dict()
        restored_event = DomainEvent.from_dict(event_dict)
        
        assert restored_event == original_event
        assert restored_event.timestamp == original_event.timestamp
    
    def test_to_json_string(self):
        """Should serialize to JSON string."""
        event = DomainEvent(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            event_id="test-event-123"
        )
        
        json_str = event.to_json()
        
        assert isinstance(json_str, str)
        assert "test-event-123" in json_str
        assert "2023-01-01T12:00:00" in json_str
    
    def test_from_json_string(self):
        """Should deserialize from JSON string."""
        json_str = '{"event_id": "test-event-123", "timestamp": "2023-01-01T12:00:00", "event_type": "DomainEvent"}'
        
        event = DomainEvent.from_json(json_str)
        
        assert event.event_id == "test-event-123"
        assert event.timestamp == datetime(2023, 1, 1, 12, 0, 0)


class TestDomainEventMetadata:
    """Test DomainEvent metadata and context information."""
    
    def test_event_age_calculation(self):
        """Should calculate event age from timestamp."""
        past_time = datetime.now() - timedelta(hours=2)
        event = DomainEvent(timestamp=past_time)
        
        age = event.age()
        
        # Should be approximately 2 hours (allow some tolerance)
        assert abs(age.total_seconds() - 7200) < 60  # Within 1 minute tolerance
    
    def test_is_recent_check(self):
        """Should identify recent events."""
        recent_event = DomainEvent()  # Created now
        old_event = DomainEvent(timestamp=datetime.now() - timedelta(hours=2))
        
        assert recent_event.is_recent(within_minutes=5)
        assert not old_event.is_recent(within_minutes=5)
    
    def test_event_type_identification(self):
        """Should identify event type."""
        event = DomainEvent()
        
        assert event.event_type() == "DomainEvent"
    
    def test_event_context_support(self):
        """Should support additional context metadata."""
        context = {
            "user_id": "user-123",
            "correlation_id": "correlation-456",
            "source_system": "trading-app"
        }
        
        event = DomainEvent(context=context)
        
        assert event.context == context
        assert event.get_context_value("user_id") == "user-123"
        assert event.get_context_value("non_existent") is None
        assert event.get_context_value("non_existent", "default") == "default"


class TestDomainEventOrdering:
    """Test DomainEvent ordering and sequencing."""
    
    def test_events_ordered_by_timestamp(self):
        """Should be orderable by timestamp."""
        time1 = datetime(2023, 1, 1, 10, 0, 0)
        time2 = datetime(2023, 1, 1, 11, 0, 0)
        time3 = datetime(2023, 1, 1, 12, 0, 0)
        
        event1 = DomainEvent(timestamp=time2, event_id="event-2")
        event2 = DomainEvent(timestamp=time1, event_id="event-1")
        event3 = DomainEvent(timestamp=time3, event_id="event-3")
        
        events = [event1, event2, event3]
        sorted_events = sorted(events)
        
        assert sorted_events[0].event_id == "event-1"
        assert sorted_events[1].event_id == "event-2"
        assert sorted_events[2].event_id == "event-3"
    
    def test_events_comparison_operators(self):
        """Should support comparison operators for ordering."""
        time1 = datetime(2023, 1, 1, 10, 0, 0)
        time2 = datetime(2023, 1, 1, 11, 0, 0)
        
        earlier_event = DomainEvent(timestamp=time1)
        later_event = DomainEvent(timestamp=time2)
        
        assert earlier_event < later_event
        assert later_event > earlier_event
        assert earlier_event <= later_event
        assert later_event >= earlier_event
        assert not earlier_event > later_event
        assert not later_event < earlier_event
    
    def test_sequence_number_support(self):
        """Should support sequence numbers for ordering within same timestamp."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        event1 = DomainEvent(timestamp=timestamp, sequence_number=1)
        event2 = DomainEvent(timestamp=timestamp, sequence_number=2)
        event3 = DomainEvent(timestamp=timestamp, sequence_number=3)
        
        events = [event2, event3, event1]
        sorted_events = sorted(events)
        
        assert sorted_events[0].sequence_number == 1
        assert sorted_events[1].sequence_number == 2
        assert sorted_events[2].sequence_number == 3


class TestDomainEventValidation:
    """Test DomainEvent validation and constraints."""
    
    def test_future_timestamp_validation(self):
        """Should validate against future timestamps when configured."""
        future_time = datetime.now() + timedelta(hours=1)
        
        # Should allow future timestamps by default
        event = DomainEvent(timestamp=future_time)
        assert event.timestamp == future_time
        
        # Should reject future timestamps when strict validation enabled
        with pytest.raises(ValueError, match="Event timestamp cannot be in the future"):
            DomainEvent(timestamp=future_time, strict_validation=True)
    
    def test_event_id_format_validation(self):
        """Should validate event ID format when configured."""
        # Should allow any string by default
        event = DomainEvent(event_id="any-string-format")
        assert event.event_id == "any-string-format"
        
        # Should validate UUID format when strict validation enabled
        with pytest.raises(ValueError, match="Event ID must be valid UUID format"):
            DomainEvent(event_id="invalid-uuid", strict_validation=True)
    
    def test_immutability_enforcement(self):
        """Should be immutable after creation."""
        event = DomainEvent()
        
        # Should not be able to modify timestamp
        with pytest.raises(AttributeError):
            event.timestamp = datetime.now()
        
        # Should not be able to modify event_id
        with pytest.raises(AttributeError):
            event.event_id = "new-id"
    
    def test_required_fields_validation(self):
        """Should validate required fields are present."""
        # timestamp and event_id are required
        event = DomainEvent()
        
        assert event.timestamp is not None
        assert event.event_id is not None
        assert len(event.event_id) > 0


class TestDomainEventInheritance:
    """Test DomainEvent inheritance and specialization."""
    
    def test_concrete_event_inheritance(self):
        """Should support inheritance for concrete event types."""
        
        class UserLoggedInEvent(DomainEvent):
            def __init__(self, user_id: str, **kwargs):
                super().__init__(**kwargs)
                self.user_id = user_id
            
            def event_type(self) -> str:
                return "UserLoggedInEvent"
        
        event = UserLoggedInEvent(user_id="user-123")
        
        assert isinstance(event, DomainEvent)
        assert event.user_id == "user-123"
        assert event.event_type() == "UserLoggedInEvent"
        assert hasattr(event, 'timestamp')
        assert hasattr(event, 'event_id')
    
    def test_polymorphic_event_handling(self):
        """Should support polymorphic handling of different event types."""
        
        class OrderCreatedEvent(DomainEvent):
            def __init__(self, order_id: str, **kwargs):
                super().__init__(**kwargs)
                self.order_id = order_id
        
        class OrderCancelledEvent(DomainEvent):
            def __init__(self, order_id: str, reason: str, **kwargs):
                super().__init__(**kwargs)
                self.order_id = order_id
                self.reason = reason
        
        events = [
            OrderCreatedEvent(order_id="order-1"),
            OrderCancelledEvent(order_id="order-2", reason="Customer request"),
            DomainEvent()
        ]
        
        # Should all be treatable as DomainEvent
        for event in events:
            assert isinstance(event, DomainEvent)
            assert hasattr(event, 'timestamp')
            assert hasattr(event, 'event_id')
    
    def test_event_hierarchy_serialization(self):
        """Should support serialization of event hierarchies."""
        
        class ProductUpdatedEvent(DomainEvent):
            def __init__(self, product_id: str, changes: dict, **kwargs):
                super().__init__(**kwargs)
                self.product_id = product_id
                self.changes = changes
            
            def to_dict(self) -> dict:
                base_dict = super().to_dict()
                base_dict.update({
                    "product_id": self.product_id,
                    "changes": self.changes
                })
                return base_dict
        
        event = ProductUpdatedEvent(
            product_id="product-123",
            changes={"price": 99.99, "stock": 10}
        )
        
        event_dict = event.to_dict()
        
        assert event_dict["product_id"] == "product-123"
        assert event_dict["changes"]["price"] == 99.99
        assert "timestamp" in event_dict
        assert "event_id" in event_dict