"""TargetStatus value object for the StockBook domain.

Represents target status with validation rules and immutability.
"""

from typing import Any, ClassVar


class TargetStatus:
    """Value object representing a target status.

    Encapsulates validation logic for target statuses and ensures immutability.
    Valid statuses are: active, hit, failed, cancelled.
    """

    VALID_STATUSES: ClassVar[set[str]] = {"active", "hit", "failed", "cancelled"}
    _value: str

    def __init__(self, value: str) -> None:
        """Initialize TargetStatus with validation.

        Args:
            value: The target status string

        Raises:
            TypeError: If value is not a string
            ValueError: If status is not valid
        """
        # Normalize to lowercase
        normalized_value = value.strip().lower()

        if normalized_value not in self.VALID_STATUSES:
            valid_list = ", ".join(sorted(self.VALID_STATUSES))
            raise ValueError(f"Target status must be one of: {valid_list}")

        # Store as private attribute to prevent mutation
        object.__setattr__(self, "_value", normalized_value)

    @property
    def value(self) -> str:
        """Get the target status value."""
        return self._value

    def __str__(self) -> str:
        """String representation of the target status."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation of the target status."""
        return f"TargetStatus({self._value!r})"

    def __eq__(self, other: Any) -> bool:
        """Check equality based on value."""
        if not isinstance(other, TargetStatus):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in collections."""
        return hash(self._value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutation after initialization."""
        if hasattr(self, "_value"):
            raise AttributeError("TargetStatus is immutable")
        super().__setattr__(name, value)
