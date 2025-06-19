"""
Stock Data Transfer Object.

Provides a clean contract for transferring stock data between
application layer and presentation layer.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StockDto:
    """
    Immutable data transfer object for stock information.

    Contains all stock data needed by the presentation layer
    without exposing domain entity internals.
    """

    id: Optional[int]
    symbol: str
    name: str
    sector: Optional[str] = None
    industry_group: Optional[str] = None
    grade: Optional[str] = None
    notes: str = ""

    def __post_init__(self):
        """Validate DTO data after initialization."""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")

        if not self.name:
            raise ValueError("Name cannot be empty")

        if self.id is not None and self.id <= 0:
            raise ValueError("ID must be positive")

    @classmethod
    def from_entity(cls, entity) -> "StockDto":
        """
        Create DTO from domain entity.

        Args:
            entity: StockEntity instance

        Returns:
            StockDto instance
        """
        # Import here to avoid circular dependency
        from domain.entities.stock_entity import StockEntity

        if not isinstance(entity, StockEntity):
            raise TypeError("Expected StockEntity instance")

        return cls(
            id=entity.id,
            symbol=str(entity.symbol),
            name=entity.company_name.value,
            sector=entity.sector.value if entity.sector else None,
            industry_group=(
                entity.industry_group.value if entity.industry_group else None
            ),
            grade=entity.grade.value if entity.grade else None,
            notes=entity.notes.value,
        )
