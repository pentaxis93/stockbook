"""Target aggregate root entity.

Rich domain entity implementing clean architecture with value objects.
Follows Domain-Driven Design principles with business logic encapsulation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from src.domain.entities.entity import Entity
from src.domain.value_objects import Money, Notes, TargetStatus


if TYPE_CHECKING:
    from datetime import date


class Target(Entity):
    """Target aggregate root representing investment price targets.

    Rich domain entity with value objects and business logic.
    Follows clean architecture and Domain-Driven Design principles.
    """

    class Builder:
        """Builder for Target to manage multiple parameters elegantly."""

        def __init__(self) -> None:
            """Initialize builder with default values."""
            self.portfolio_id: str | None = None
            self.stock_id: str | None = None
            self.pivot_price: Money | None = None
            self.failure_price: Money | None = None
            self.status: TargetStatus | None = None
            self.created_date: date | None = None
            self.notes: Notes | None = None
            self.entity_id: str | None = None

        def with_portfolio_id(self, portfolio_id: str) -> Self:
            """Set the portfolio ID."""
            self.portfolio_id = portfolio_id
            return self

        def with_stock_id(self, stock_id: str) -> Self:
            """Set the stock ID."""
            self.stock_id = stock_id
            return self

        def with_pivot_price(self, pivot_price: Money) -> Self:
            """Set the pivot price."""
            self.pivot_price = pivot_price
            return self

        def with_failure_price(self, failure_price: Money) -> Self:
            """Set the failure price."""
            self.failure_price = failure_price
            return self

        def with_status(self, status: TargetStatus) -> Self:
            """Set the target status."""
            self.status = status
            return self

        def with_created_date(self, created_date: date) -> Self:
            """Set the created date."""
            self.created_date = created_date
            return self

        def with_notes(self, notes: Notes | None) -> Self:
            """Set the notes."""
            self.notes = notes
            return self

        def with_id(self, entity_id: str | None) -> Self:
            """Set the entity ID."""
            self.entity_id = entity_id
            return self

        def build(self) -> Target:
            """Build and return the Target instance."""
            return Target(_builder_instance=self)

    def __init__(self, *, _builder_instance: Target.Builder | None = None):
        """Initialize target through builder pattern."""
        if _builder_instance is None:
            raise ValueError("Target must be created through Builder")

        # Extract values from builder
        portfolio_id = _builder_instance.portfolio_id
        stock_id = _builder_instance.stock_id
        pivot_price = _builder_instance.pivot_price
        failure_price = _builder_instance.failure_price
        status = _builder_instance.status
        created_date = _builder_instance.created_date
        notes = _builder_instance.notes
        entity_id = _builder_instance.entity_id

        # Validate required fields
        if portfolio_id is None:
            raise ValueError("Portfolio ID is required")
        if stock_id is None:
            raise ValueError("Stock ID is required")
        if pivot_price is None:
            raise ValueError("Pivot price is required")
        if failure_price is None:
            raise ValueError("Failure price is required")
        if status is None:
            raise ValueError("Status is required")
        if created_date is None:
            raise ValueError("Created date is required")

        # Validate foreign key IDs are not empty
        if not portfolio_id:
            raise ValueError("Portfolio ID must be a non-empty string")
        if not stock_id:
            raise ValueError("Stock ID must be a non-empty string")

        # Store validated attributes
        super().__init__(id=entity_id)
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
        return (
            f"Target(pivot: {self._pivot_price}, failure: {self._failure_price}, "
            f"status={self._status.value})"
        )

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"Target(portfolio_id={self._portfolio_id}, stock_id={self._stock_id}, "
            f"status={self._status.value!r})"
        )
