"""
Value objects used by domain services.

These value objects encapsulate the results and parameters of domain service
operations, providing type-safe and immutable data structures.
"""

from .portfolio_metrics import PortfolioMetrics, PortfolioAllocation, PortfolioSummary
from .risk_metrics import RiskProfile, RiskLevel, RiskMetrics, PortfolioRisk

# from .diversification_metrics import DiversificationScore, SectorAllocation, CorrelationMatrix
# from .price_analysis import PriceAnalysis, PriceAlert, PriceTrend

__all__ = [
    "PortfolioMetrics",
    "PortfolioAllocation",
    "PortfolioSummary",
    "RiskProfile",
    "RiskLevel",
    "RiskMetrics",
    "PortfolioRisk",
    # 'DiversificationScore',
    # 'SectorAllocation',
    # 'CorrelationMatrix',
    # 'PriceAnalysis',
    # 'PriceAlert',
    # 'PriceTrend'
]
