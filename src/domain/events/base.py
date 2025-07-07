"""Base domain event infrastructure.

Provides the foundation for domain events that enable
loose coupling between aggregates and bounded contexts.
"""

import uuid
from datetime import UTC, datetime
from typing import Any


class DomainEvent:
    """Base class for all domain events.

    Domain events represent significant business occurrences
    that other parts of the system may need to react to.
    """

    def __init__(self, occurred_at: datetime | None = None) -> None:
        """Initialize domain event.

        Args:
            occurred_at: When the event occurred (defaults to now)
        """
        self._event_id = str(uuid.uuid4())
        self._occurred_at = occurred_at or datetime.now(UTC)

    @property
    def event_id(self) -> str:
        """Get unique event identifier."""
        return self._event_id

    @property
    def occurred_at(self) -> datetime:
        """Get when the event occurred."""
        return self._occurred_at

    def __eq__(self, other: Any) -> bool:
        """Check equality based on event ID."""
        if not isinstance(other, DomainEvent):
            return False
        return self.event_id == other.event_id

    def __hash__(self) -> int:
        """Hash based on event ID."""
        return hash(self.event_id)

    def __str__(self) -> str:
        """String representation for display."""
        return f"{self.__class__.__name__}(id={self.event_id})"

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"{self.__class__.__name__}(event_id={self.event_id!r}, "
            f"occurred_at={self.occurred_at.isoformat()})"
        )
