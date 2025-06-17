"""
Base domain event infrastructure for the shared kernel.

Provides foundational event system that all bounded contexts can build upon.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


class DomainEvent:
    """
    Base class for all domain events in the system.

    Provides common event infrastructure including timestamps, unique IDs,
    serialization, and metadata handling that all domain events need.
    """

    def __init__(
        self,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        sequence_number: Optional[int] = None,
        strict_validation: bool = False,
    ):
        """
        Initialize domain event with metadata.

        Args:
            timestamp: Event occurrence time (defaults to now)
            event_id: Unique event identifier (defaults to UUID)
            context: Additional context metadata
            sequence_number: Sequence number for ordering within same timestamp
            strict_validation: Enable strict validation of inputs

        Raises:
            ValueError: If strict validation enabled and inputs are invalid
        """
        # Validate timestamp if strict validation enabled
        if strict_validation and timestamp and timestamp > datetime.now():
            raise ValueError("Event timestamp cannot be in the future")

        self._timestamp = timestamp or datetime.now()

        # Generate or validate event ID
        if event_id is None:
            self._event_id = str(uuid.uuid4())
        else:
            if strict_validation:
                try:
                    uuid.UUID(event_id)
                except ValueError:
                    raise ValueError("Event ID must be valid UUID format")
            self._event_id = event_id

        self._context = context or {}
        self._sequence_number = sequence_number

    @property
    def timestamp(self) -> datetime:
        """Get the event timestamp."""
        return self._timestamp

    @property
    def event_id(self) -> str:
        """Get the unique event identifier."""
        return self._event_id

    @property
    def context(self) -> Dict[str, Any]:
        """Get the event context metadata."""
        return self._context.copy()  # Return copy for immutability

    @property
    def sequence_number(self) -> Optional[int]:
        """Get the sequence number."""
        return self._sequence_number

    def __eq__(self, other) -> bool:
        """Equality based on event ID."""
        if not isinstance(other, DomainEvent):
            return False
        return self._event_id == other._event_id

    def __hash__(self) -> int:
        """Hash based on event ID."""
        return hash(self._event_id)

    def __lt__(self, other) -> bool:
        """Ordering by timestamp, then by sequence number."""
        if not isinstance(other, DomainEvent):
            return NotImplemented

        if self._timestamp != other._timestamp:
            return self._timestamp < other._timestamp

        # If timestamps are equal, use sequence number
        if self._sequence_number is not None and other._sequence_number is not None:
            return self._sequence_number < other._sequence_number

        # If no sequence numbers, maintain stable ordering by event_id
        return self._event_id < other._event_id

    def __le__(self, other) -> bool:
        """Less than or equal ordering."""
        return self == other or self < other

    def __gt__(self, other) -> bool:
        """Greater than ordering."""
        if not isinstance(other, DomainEvent):
            return NotImplemented
        return not self <= other

    def __ge__(self, other) -> bool:
        """Greater than or equal ordering."""
        return self == other or self > other

    def age(self) -> timedelta:
        """Calculate age of event from its timestamp."""
        return datetime.now() - self._timestamp

    def is_recent(self, within_minutes: int = 5) -> bool:
        """Check if event occurred within specified minutes."""
        age_minutes = self.age().total_seconds() / 60
        return age_minutes <= within_minutes

    def event_type(self) -> str:
        """Get the event type name."""
        return self.__class__.__name__

    def get_context_value(self, key: str, default: Any = None) -> Any:
        """Get value from event context."""
        return self._context.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary."""
        result = {
            "event_id": self._event_id,
            "timestamp": self._timestamp.isoformat(),
            "event_type": self.event_type(),
        }

        if self._context:
            result["context"] = self._context

        if self._sequence_number is not None:
            result["sequence_number"] = self._sequence_number

        return result

    def to_json(self) -> str:
        """Serialize event to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, event_dict: Dict[str, Any]) -> "DomainEvent":
        """Deserialize event from dictionary."""
        timestamp_str = event_dict.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None

        return cls(
            timestamp=timestamp,
            event_id=event_dict.get("event_id"),
            context=event_dict.get("context"),
            sequence_number=event_dict.get("sequence_number"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "DomainEvent":
        """Deserialize event from JSON string."""
        event_dict = json.loads(json_str)
        return cls.from_dict(event_dict)
