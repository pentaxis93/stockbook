"""
Value objects for price analysis results.

Immutable data structures that represent the results of price analysis
and pricing service operations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from domain.value_objects.stock_symbol import StockSymbol
from shared_kernel.value_objects import Money


class TrendDirection(Enum):
    """Price trend direction enumeration."""

    UPWARD = "upward"
    DOWNWARD = "downward"
    SIDEWAYS = "sideways"


class AlertType(Enum):
    """Price alert type enumeration."""

    PRICE_THRESHOLD = "price_threshold"
    PERCENTAGE_CHANGE = "percentage_change"
    HIGH_VOLATILITY = "high_volatility"
    TECHNICAL_INDICATOR = "technical_indicator"


@dataclass(frozen=True)
class PriceTrend:
    """Represents price trend analysis."""

    direction: TrendDirection
    strength: Decimal  # 0-1 scale
    duration_days: int
    confidence_level: Decimal  # 0-1 scale

    @property
    def is_strong_trend(self) -> bool:
        """Check if trend is considered strong."""
        return self.strength >= Decimal("0.7") and self.confidence_level >= Decimal(
            "0.8"
        )


@dataclass(frozen=True)
class PriceAlert:
    """Represents a price-related alert."""

    symbol: StockSymbol
    alert_type: AlertType
    message: str
    current_price: Money
    trigger_value: Optional[Money] = None
    timestamp: Optional[datetime] = None
    severity: str = "medium"  # low, medium, high

    def __post_init__(self):
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now())


@dataclass(frozen=True)
class PriceAnalysis:
    """Comprehensive price analysis results."""

    symbol: StockSymbol
    current_price: Money
    trend_analysis: PriceTrend
    support_levels: List[Money]
    resistance_levels: List[Money]
    volatility_score: Decimal  # 0-1 scale
    momentum_indicators: Dict[str, Decimal]
    alerts: List[PriceAlert]

    @property
    def is_overbought(self) -> bool:
        """Check if stock appears overbought."""
        rsi = self.momentum_indicators.get("rsi", Decimal("50"))
        return rsi >= Decimal("70")

    @property
    def is_oversold(self) -> bool:
        """Check if stock appears oversold."""
        rsi = self.momentum_indicators.get("rsi", Decimal("50"))
        return rsi <= Decimal("30")
