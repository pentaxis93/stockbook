"""
Base entity class for domain entities.

Provides common functionality for all domain entities following DDD principles.
"""

from abc import ABC
from typing import Any, Optional


class BaseEntity(ABC):
    """Base class for all domain entities with common functionality."""

    def __init__(self) -> None:
        self._id: Optional[int] = None

    @property
    def id(self) -> Optional[int]:
        """Get entity ID."""
        return self._id

    # Is set_id() needed? The id is a primary key in the database.
    # That means it will be set by the database and not by the user.
    def set_id(self, entity_id: int) -> None:
        """Set entity ID (for persistence layer)."""
        if not isinstance(entity_id, int) or entity_id <= 0:
            raise ValueError("ID must be a positive integer")
        if self._id is not None:
            raise ValueError("ID is already set and cannot be changed")
        self._id = entity_id

    def __eq__(self, other: Any) -> bool:
        """Entities are equal if they are the same type and have the same ID."""
        if not isinstance(other, self.__class__):
            return False
        return self._id == other._id and self._id is not None

    def __str__(self) -> str:
        """String representation of entity."""
        class_name = self.__class__.__name__
        if self._id is not None:
            return f"{class_name}(id={self._id})"
        return f"{class_name}(id=None)"

    def __repr__(self) -> str:
        """Detailed string representation of entity."""
        return self.__str__()
