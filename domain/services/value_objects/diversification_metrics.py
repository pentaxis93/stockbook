"""
Value objects for diversification analysis results.

Immutable data structures that represent the results of diversification
analysis and correlation calculations.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

from domain.value_objects.stock_symbol import StockSymbol
from shared_kernel.value_objects import Money


@dataclass(frozen=True)
class SectorAllocation:
    """Represents allocation across different sectors."""

    allocations: Dict[str, Decimal]  # Sector -> percentage
    total_value: Money

    def get_sector_percentage(self, sector: str) -> Decimal:
        """Get allocation percentage for a specific sector."""
        return self.allocations.get(sector, Decimal("0"))


@dataclass(frozen=True)
class CorrelationMatrix:
    """Represents correlation coefficients between stocks."""

    correlations: Dict[tuple, Decimal]  # (symbol1, symbol2) -> correlation

    def get_correlation(self, symbol1: str, symbol2: str) -> Decimal:
        """Get correlation coefficient between two stocks."""
        key1 = (symbol1, symbol2)
        key2 = (symbol2, symbol1)

        if key1 in self.correlations:
            return self.correlations[key1]
        elif key2 in self.correlations:
            return self.correlations[key2]
        else:
            return Decimal("0")


@dataclass(frozen=True)
class DiversificationScore:
    """Comprehensive diversification scoring."""

    overall_score: Decimal  # 0-1 scale
    sector_score: Decimal
    market_cap_score: Decimal
    correlation_score: Decimal
    geographic_score: Optional[Decimal] = None

    @property
    def letter_grade(self) -> str:
        """Convert score to letter grade."""
        if self.overall_score >= Decimal("0.9"):
            return "A+"
        elif self.overall_score >= Decimal("0.8"):
            return "A"
        elif self.overall_score >= Decimal("0.7"):
            return "B+"
        elif self.overall_score >= Decimal("0.6"):
            return "B"
        elif self.overall_score >= Decimal("0.5"):
            return "C+"
        elif self.overall_score >= Decimal("0.4"):
            return "C"
        else:
            return "D"
