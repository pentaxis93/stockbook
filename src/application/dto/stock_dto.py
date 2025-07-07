"""Stock Data Transfer Object.

Provides a clean contract for transferring stock data between
application layer and presentation layer.
"""

from dataclasses import dataclass
from typing import Any

from src.domain.entities.stock import Stock


@dataclass(frozen=True)
class StockDto:
    """Immutable data transfer object for stock information.

    Contains all stock data needed by the presentation layer
    without exposing domain entity internals.
    """

    id: str | None
    symbol: str
    name: str | None = None
    sector: str | None = None
    industry_group: str | None = None
    grade: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        """Validate DTO data after initialization."""
        if not self.symbol:
            msg = "Symbol cannot be empty"
            raise ValueError(msg)

        if self.id is not None and not self.id:
            msg = "ID must be a string"
            raise ValueError(msg)

    @classmethod
    def from_entity(cls, entity: Any) -> "StockDto":
        """Create DTO from domain entity.

        Args:
            entity: Stock instance

        Returns:
            StockDto instance
        """
        if not isinstance(entity, Stock):
            msg = "Expected Stock instance"
            raise TypeError(msg)

        return cls(
            id=entity.id,
            symbol=str(entity.symbol),
            name=entity.company_name.value if entity.company_name else None,
            sector=entity.sector.value if entity.sector else None,
            industry_group=(
                entity.industry_group.value if entity.industry_group else None
            ),
            grade=entity.grade.value if entity.grade else None,
            notes=entity.notes.value,
        )
