"""
Target aggregate root entity.

Rich domain entity implementing clean architecture with value objects.
Follows Domain-Driven Design principles with business logic encapsulation.
"""

from datetime import date

from src.domain.entities.entity import Entity
from src.domain.value_objects import Money, Notes, TargetStatus


class Target(Entity):
    """
    Target aggregate root representing investment price targets.

    Rich domain entity with value objects and business logic.
    Follows clean architecture and Domain-Driven Design principles.
    """

    def __init__(  # pylint: disable=too-many-arguments
        # Rationale: Target is a domain entity representing investment price targets.
        # Each parameter is essential: portfolio/stock references, pivot/failure prices,
        # status tracking, and creation date. Using a parameter object would reduce
        # clarity without meaningful benefit for this investment tracking concept.
        self,
        portfolio_id: str,
        stock_id: str,
        pivot_price: Money,
        failure_price: Money,
        status: TargetStatus,
        created_date: date,
        *,
        notes: Notes | None = None,
        id: str | None = None,
    ):
        """Initialize target with required value objects and validation."""
        # Validate foreign key IDs are not empty
        if not portfolio_id:
            raise ValueError("Portfolio ID must be a non-empty string")
        if not stock_id:
            raise ValueError("Stock ID must be a non-empty string")

        # Store validated attributes
        super().__init__(id=id)
        self._portfolio_id = portfolio_id
        self._stock_id = stock_id
        self._pivot_price = pivot_price
        self._failure_price = failure_price
        self._status = status
        self._created_date = created_date
        self._notes = notes or Notes("")

    @property
    def portfolio_id(self) -> str:
        """Get portfolio ID."""
        return self._portfolio_id

    @property
    def stock_id(self) -> str:
        """Get stock ID."""
        return self._stock_id

    # Core attributes
    @property
    def pivot_price(self) -> Money:
        """Get pivot price."""
        return self._pivot_price

    @property
    def failure_price(self) -> Money:
        """Get failure price."""
        return self._failure_price

    @property
    def status(self) -> TargetStatus:
        """Get target status."""
        return self._status

    @property
    def created_date(self) -> date:
        """Get created date."""
        return self._created_date

    @property
    def notes(self) -> Notes:
        """Get notes."""
        return self._notes

    # Business methods
    def activate(self) -> None:
        """Activate the target."""
        self._status = TargetStatus("active")

    def mark_as_hit(self) -> None:
        """Mark the target as hit."""
        self._status = TargetStatus("hit")

    def mark_as_failed(self) -> None:
        """Mark the target as failed."""
        self._status = TargetStatus("failed")

    def cancel(self) -> None:
        """Cancel the target."""
        self._status = TargetStatus("cancelled")

    def is_active(self) -> bool:
        """Check if target is active."""
        return self._status.value == "active"

    def is_hit(self) -> bool:
        """Check if target is hit."""
        return self._status.value == "hit"

    def is_failed(self) -> bool:
        """Check if target is failed."""
        return self._status.value == "failed"

    def is_cancelled(self) -> bool:
        """Check if target is cancelled."""
        return self._status.value == "cancelled"

    def has_notes(self) -> bool:
        """Check if target has non-empty notes."""
        return self._notes.has_content()

    def update_notes(self, notes: Notes | str) -> None:
        """Update target notes."""
        if isinstance(notes, str):
            self._notes = Notes(notes)
        else:
            self._notes = notes

    # Representation

    def __str__(self) -> str:
        """String representation."""
        return f"Target(pivot: {self._pivot_price}, failure: {self._failure_price}, status={self._status.value})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Target(portfolio_id={self._portfolio_id}, stock_id={self._stock_id}, status={self._status.value!r})"
