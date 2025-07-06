"""Base entity class for domain entities.

Provides common functionality for all domain entities following DDD principles.
"""

import uuid
from abc import ABC
from typing import Any, Self, TypeVar

T = TypeVar("T", bound="Entity")


class Entity(ABC):  # noqa: B024
    """Base class for all domain entities with immutable string IDs."""

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent direct instantiation of Entity base class."""
        if cls is Entity:
            raise TypeError("Can't instantiate abstract class Entity directly")
        return super().__new__(cls)

    def __init__(self, id: str | None = None) -> None:
        """Initialize entity with either provided ID or generate new UUID."""
        self._id: str = id if id is not None else str(uuid.uuid4())

    @property
    def id(self) -> str:
        """Get entity ID."""
        return self._id

    @classmethod
    def from_persistence(cls: type[Self], id: str, **kwargs: Any) -> Self:
        """Create entity from persistence layer with existing ID."""
        # This will call the subclass constructor with the id parameter
        return cls(id=id, **kwargs)

    def __eq__(self, other: Any) -> bool:
        """Entities are equal if they are the same type and have the same ID."""
        if not isinstance(other, self.__class__):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Hash based on entity ID for use in collections."""
        return hash(self._id)

    def __str__(self) -> str:
        """String representation of entity."""
        class_name = self.__class__.__name__
        return f"{class_name}(id={self._id})"

    def __repr__(self) -> str:
        """Detailed string representation of entity showing all public attributes."""
        class_name = self.__class__.__name__

        # Collect all public attributes (not starting with _)
        attrs: list[str] = []
        for key in sorted(dir(self)):
            if not key.startswith("_") and not callable(getattr(self, key)):
                value = getattr(self, key)
                if isinstance(value, str):
                    attrs.append(f"{key}='{value}'")
                else:
                    attrs.append(f"{key}={value}")

        return f"{class_name}({', '.join(attrs)})"
