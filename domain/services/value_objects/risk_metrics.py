"""
Value objects for risk assessment results.

Immutable data structures that represent risk analysis results
and risk-related calculations.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from shared_kernel.value_objects import Money
from domain.value_objects.stock_symbol import StockSymbol


class RiskLevel(Enum):
    """Risk level enumeration."""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ConcentrationLevel(Enum):
    """Concentration risk level enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class RiskFactor:
    """Represents a specific risk factor."""

    name: str
    description: str
    risk_level: RiskLevel
    impact_score: Decimal  # 0-10 scale
    mitigation_suggestions: List[str]


@dataclass(frozen=True)
class RiskProfile:
    """Individual stock risk profile."""

    symbol: StockSymbol
    overall_risk_level: RiskLevel
    volatility_risk: RiskLevel
    beta_risk: RiskLevel
    fundamental_risk: RiskLevel
    sector_risk: RiskLevel
    risk_factors: List[RiskFactor]
    risk_score: Decimal  # 0-100 scale

    @property
    def is_high_risk(self) -> bool:
        """Check if stock is considered high risk."""
        return self.overall_risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]


@dataclass(frozen=True)
class ConcentrationRisk:
    """Represents concentration risk in portfolio."""

    type: str  # "position", "sector", "geography", etc.
    category: str  # Specific category (e.g., "Technology", "AAPL")
    concentration_level: ConcentrationLevel
    percentage: Decimal
    risk_description: str
    recommended_action: str


@dataclass(frozen=True)
class RiskMetrics:
    """Portfolio-level risk metrics."""

    overall_risk_level: RiskLevel
    weighted_beta: Decimal
    portfolio_volatility: Decimal
    var_95_percent: Money  # Value at Risk (95% confidence)
    cvar_95_percent: Money  # Conditional Value at Risk
    sharpe_ratio: Optional[Decimal]
    maximum_drawdown: Optional[Decimal]
    concentration_risks: List[ConcentrationRisk]
    risk_score: Decimal  # 0-100 scale

    @property
    def requires_attention(self) -> bool:
        """Check if portfolio risk requires immediate attention."""
        return (
            self.overall_risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]
            or len(
                [
                    r
                    for r in self.concentration_risks
                    if r.concentration_level == ConcentrationLevel.CRITICAL
                ]
            )
            > 0
        )


@dataclass(frozen=True)
class PortfolioRisk:
    """Comprehensive portfolio risk assessment."""

    portfolio_metrics: RiskMetrics
    individual_stock_risks: List[RiskProfile]
    sector_risks: Dict[str, RiskLevel]
    geographic_risks: Dict[str, RiskLevel]
    correlation_risks: List[str]  # Description of correlation-based risks
    stress_test_results: Dict[str, Decimal]  # Scenario -> loss percentage
    risk_warnings: List[str]
    mitigation_strategies: List[str]

    def get_highest_risk_stocks(self, limit: int = 5) -> List[RiskProfile]:
        """Get the highest risk stocks in portfolio."""
        return sorted(
            self.individual_stock_risks, key=lambda x: x.risk_score, reverse=True
        )[:limit]
