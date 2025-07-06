"""Consolidated value objects for portfolio analysis and metrics.

Simple, focused data structures that represent the results of portfolio
calculations, risk assessment, and analysis operations.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from src.domain.value_objects import Money
from src.domain.value_objects.stock_symbol import StockSymbol


# Enumerations
class RiskLevel(Enum):
    """Risk level enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TrendDirection(Enum):
    """Price trend direction enumeration."""

    UPWARD = "upward"
    DOWNWARD = "downward"
    SIDEWAYS = "sideways"


# Core Metrics
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
class PortfolioAllocation:
    """Represents allocation breakdown by different categories."""

    allocations: dict[str, Decimal]  # Category -> percentage
    total_value: Money

    def get_allocation_percentage(self, category: str) -> Decimal:
        """Get allocation percentage for a specific category."""
        return self.allocations.get(category, Decimal("0"))


@dataclass(frozen=True)
class PortfolioMetrics:
    """Essential portfolio metrics and calculations."""

    total_value: Money
    position_count: int
    position_allocations: list[PositionAllocation]
    industry_allocation: PortfolioAllocation

    # Class constant for diversification threshold
    DIVERSIFICATION_THRESHOLD = 5

    @property
    def largest_position(self) -> PositionAllocation | None:
        """Get the largest position by value."""
        if not self.position_allocations:
            return None
        return max(self.position_allocations, key=lambda pos: pos.value.amount)

    @property
    def is_well_diversified(self) -> bool:
        """Check if portfolio meets basic diversification criteria."""
        return self.position_count >= self.DIVERSIFICATION_THRESHOLD and not any(
            pos.is_overweight for pos in self.position_allocations
        )


@dataclass(frozen=True)
class RiskAssessment:
    """Simple risk assessment for portfolio or individual positions."""

    overall_risk_level: RiskLevel
    risk_score: Decimal  # 0-100 scale
    risk_factors: list[str]  # Simple list of risk descriptions

    @property
    def is_high_risk(self) -> bool:
        """Check if assessed as high risk."""
        return self.overall_risk_level == RiskLevel.HIGH


@dataclass(frozen=True)
class PriceAnalysis:
    """Basic price analysis results."""

    symbol: StockSymbol
    current_price: Money
    trend_direction: TrendDirection
    volatility_score: Decimal  # 0-1 scale

    @property
    def is_volatile(self) -> bool:
        """Check if stock is considered volatile."""
        return self.volatility_score >= Decimal("0.7")
