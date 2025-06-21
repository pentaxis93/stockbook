"""
Base entity class for domain entities.

Provides common functionality for all domain entities following DDD principles.
"""

from abc import ABC
from typing import Any, Optional

import nanoid


class BaseEntity(ABC):
    """Base class for all domain entities with immutable string IDs."""

    def __init__(self, id: Optional[str] = None) -> None:
        """Initialize entity with either provided ID or generate new nanoid."""
        self._id: str = id if id is not None else nanoid.generate()

    @property
    def id(self) -> str:
        """Get entity ID."""
        return self._id

    @classmethod
    def from_persistence(cls, id: str, **kwargs):
        """Create entity from persistence layer with existing ID."""
        # This will call the subclass constructor with the id parameter
        return cls(id=id, **kwargs)

    def __eq__(self, other: Any) -> bool:
        """Entities are equal if they are the same type and have the same ID."""
        if not isinstance(other, self.__class__):
            return False
        return self._id == other._id

    def __str__(self) -> str:
        """String representation of entity."""
        class_name = self.__class__.__name__
        return f"{class_name}(id={self._id})"

    def __repr__(self) -> str:
        """Detailed string representation of entity."""
        return self.__str__()
