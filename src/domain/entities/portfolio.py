"""Portfolio aggregate root entity.

Rich domain entity implementing clean architecture with value objects.
Follows Domain-Driven Design principles with business logic encapsulation.
"""

from datetime import datetime

from src.domain.entities.entity import Entity
from src.domain.value_objects import Notes, PortfolioName


class Portfolio(Entity):
    """Portfolio aggregate root representing a collection of investments.

    Rich domain entity with value objects and business logic.
    Follows clean architecture and Domain-Driven Design principles.
    """

    def __init__(
        # Rationale: Portfolio is a fundamental domain entity with minimal attributes.
        # Each parameter represents essential portfolio characteristics: name,
        # description,
        # creation tracking, and active status. These cannot be simplified further.
        self,
        name: PortfolioName,
        description: Notes | None = None,
        created_date: datetime | None = None,
        is_active: bool = True,
        id: str | None = None,
    ) -> None:
        """Initialize portfolio with required value objects and validation."""
        # Store validated attributes
        super().__init__(id=id)
        self._name = name
        self._description = description or Notes("")
        self._created_date = created_date
        self._is_active = is_active

    # Core attributes
    @property
    def name(self) -> PortfolioName:
        """Get portfolio name."""
        return self._name

    @property
    def description(self) -> Notes:
        """Get portfolio description."""
        return self._description

    @property
    def created_date(self) -> datetime | None:
        """Get created date."""
        return self._created_date

    @property
    def is_active(self) -> bool:
        """Get active status."""
        return self._is_active

    # Business methods
    def activate(self) -> None:
        """Activate the portfolio."""
        self._is_active = True

    def deactivate(self) -> None:
        """Deactivate the portfolio."""
        self._is_active = False

    def is_active_portfolio(self) -> bool:
        """Check if portfolio is active."""
        return self._is_active

    def has_description(self) -> bool:
        """Check if portfolio has a non-empty description."""
        return self._description.has_content()

    def update_description(self, description: Notes | str) -> None:
        """Update portfolio description."""
        if isinstance(description, str):
            self._description = Notes(description)
        else:
            self._description = description

    def set_created_date(self, created_date: datetime) -> None:
        """Set created date (for persistence layer)."""
        if self._created_date is not None:
            msg = "Created date is already set and cannot be changed"
            raise ValueError(msg)
        self._created_date = created_date

    # Representation

    def __str__(self) -> str:
        """String representation."""
        return f"Portfolio({self._name.value})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Portfolio(name={self._name!r}, active={self._is_active})"
