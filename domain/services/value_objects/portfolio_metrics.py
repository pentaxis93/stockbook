"""
Value objects for portfolio calculation results.

Immutable data structures that represent the results of portfolio calculations
and analysis operations.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

from domain.value_objects.stock_symbol import StockSymbol
from shared_kernel.value_objects import Money


@dataclass(frozen=True)
class PortfolioAllocation:
    """Represents allocation breakdown by different categories."""

    allocations: Dict[str, Decimal]  # Category -> percentage
    total_value: Money

    def get_allocation_percentage(self, category: str) -> Decimal:
        """Get allocation percentage for a specific category."""
        return self.allocations.get(category, Decimal("0"))

    def get_allocation_value(self, category: str) -> Money:
        """Get allocation value for a specific category."""
        percentage = self.get_allocation_percentage(category)
        allocation_amount = self.total_value.amount * (percentage / Decimal("100"))
        return Money(allocation_amount, self.total_value.currency)


@dataclass(frozen=True)
class PositionAllocation:
    """Represents allocation of a single position in portfolio."""

    symbol: StockSymbol
    value: Money
    percentage: Decimal
    quantity: int

    @property
    def is_overweight(self) -> bool:
        """Check if position is overweight (>10% of portfolio)."""
        return self.percentage > Decimal("10.0")


@dataclass(frozen=True)
class PortfolioMetrics:
    """Comprehensive portfolio metrics and calculations."""

    total_value: Money
    position_count: int
    largest_position: Optional[PositionAllocation]
    smallest_position: Optional[PositionAllocation]
    average_position_size: Money
    position_allocations: List[PositionAllocation]
    industry_allocation: PortfolioAllocation
    grade_allocation: PortfolioAllocation
    weighted_average_grade: str
    diversity_score: Decimal  # 0-1 scale

    @property
    def is_well_diversified(self) -> bool:
        """Check if portfolio meets basic diversification criteria."""
        return (
            self.position_count >= 5
            and self.diversity_score >= Decimal("0.6")
            and not any(pos.is_overweight for pos in self.position_allocations)
        )


@dataclass(frozen=True)
class PortfolioSummary:
    """High-level portfolio summary for reporting."""

    total_value: Money
    position_count: int
    top_holding: Optional[PositionAllocation]
    industry_breakdown: Dict[str, Decimal]  # Industry -> percentage
    grade_breakdown: Dict[str, Decimal]  # Grade -> percentage
    risk_level: str  # "Low", "Medium", "High"
    diversification_grade: str  # A+, A, B+, etc.

    def get_top_industries(self, limit: int = 3) -> List[tuple]:
        """Get top industries by allocation percentage."""
        sorted_industries = sorted(
            self.industry_breakdown.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_industries[:limit]
