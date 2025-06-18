"""
Portfolio aggregate root entity.

Placeholder implementation for portfolio domain entity to replace
legacy Pydantic model dependency in repository interfaces.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class PortfolioEntity:
    """
    Portfolio aggregate root representing a collection of investments.

    TODO: Implement full domain entity with business logic, validation,
    and rich behavior. This is currently a placeholder to remove
    legacy model dependencies from repository interfaces.
    """

    # Identity
    id: Optional[int] = None

    # Core attributes
    name: str = ""
    description: Optional[str] = None
    created_date: Optional[date] = None
    is_active: bool = True

    def __post_init__(self):
        """Validate portfolio data after initialization."""
        if not self.name:
            raise ValueError("Portfolio name cannot be empty")

        if len(self.name) > 100:
            raise ValueError("Portfolio name cannot exceed 100 characters")

    def __str__(self) -> str:
        """String representation."""
        return f"Portfolio({self.name})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"PortfolioEntity(id={self.id}, name='{self.name}', active={self.is_active})"
