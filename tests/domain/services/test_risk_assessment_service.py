"""
Unit tests for RiskAssessmentService.

Tests business logic for comprehensive risk assessment of individual stocks
and portfolios, including various risk metrics and risk management strategies.
"""

from decimal import Decimal
from typing import Dict, List

from src.domain.entities.stock_entity import StockEntity
from src.domain.services.risk_assessment_service import (
    RiskAssessmentConfig,
    RiskAssessmentService,
)
from src.domain.services.value_objects.risk_metrics import (
    PortfolioRisk,
    RiskLevel,
    RiskProfile,
)
from src.domain.value_objects.company_name import CompanyName
from src.domain.value_objects.grade import Grade
from src.domain.value_objects.industry_group import IndustryGroup
from src.domain.value_objects.money import Money
from src.domain.value_objects.quantity import Quantity
from src.domain.value_objects.sector import Sector
from src.domain.value_objects.stock_symbol import StockSymbol


# Test data helpers
def create_test_stock(
    symbol: str,
    price: float,
    grade: str,
    industry: str = "Technology",
    volatility: float = 0.2,
    beta: float = 1.0,
) -> StockEntity:
    """Helper to create test stock with risk attributes."""
    # Map industries to sector + industry_group combinations
    industry_mapping = {
        "Technology": ("Technology", "Software"),
        "Consumer Goods": ("Consumer Goods", "Food & Beverages"),
        "Utilities": ("Energy", "Utilities"),
        "Energy": ("Energy", "Oil & Gas"),
        "Biotech": ("Healthcare", "Biotechnology"),
        "Unknown": (None, None),
    }

    sector, industry_group = industry_mapping.get(industry, ("Technology", "Software"))

    stock = StockEntity(
        symbol=StockSymbol(symbol),
        company_name=CompanyName(f"{symbol} Corp"),
        sector=Sector(sector) if sector else None,
        industry_group=IndustryGroup(industry_group) if industry_group else None,
        grade=Grade(grade) if grade else None,
    )
    # Set a numeric ID (use hash of symbol for consistency)
    stock.set_id(abs(hash(symbol)) % 1000000 + 1)
    return stock


def create_conservative_portfolio():
    """Helper to create a conservative risk portfolio."""
    return [
        (
            create_test_stock("JNJ", 160.00, "A", "Consumer Goods", 0.15, 0.8),
            Quantity(20),
        ),
        (
            create_test_stock("PG", 130.00, "A", "Consumer Goods", 0.18, 0.7),
            Quantity(15),
        ),
        (
            create_test_stock("KO", 55.00, "A", "Consumer Goods", 0.20, 0.9),
            Quantity(30),
        ),
        (create_test_stock("VZ", 40.00, "B", "Utilities", 0.22, 0.6), Quantity(25)),
    ]


def create_aggressive_portfolio():
    """Helper to create a high-risk aggressive portfolio."""
    return [
        (create_test_stock("TSLA", 200.00, "B", "Technology", 0.65, 2.1), Quantity(10)),
        (create_test_stock("NVDA", 300.00, "A", "Technology", 0.55, 1.8), Quantity(8)),
        (create_test_stock("ARKK", 50.00, "C", "Technology", 0.70, 1.5), Quantity(40)),
        (
            create_test_stock("GME", 20.00, "C", "Consumer Goods", 0.80, 2.5),
            Quantity(50),
        ),
    ]


def create_concentrated_portfolio():
    """Helper to create a portfolio with concentration risk."""
    return [
        (
            create_test_stock("AAPL", 150.00, "A", "Technology", 0.30, 1.2),
            Quantity(100),
        ),  # Large position
        (
            create_test_stock("MSFT", 250.00, "A", "Technology", 0.25, 1.1),
            Quantity(10),
        ),  # Small position
        (
            create_test_stock("GOOGL", 2500.00, "A", "Technology", 0.35, 1.3),
            Quantity(2),
        ),  # Small position
    ]


def create_test_prices(portfolio: List) -> Dict[str, Money]:
    """Helper to create price dictionary from portfolio."""
    prices = {}
    for stock, _ in portfolio:
        # Use a default price since we don't need actual prices for stub tests
        prices[str(stock.symbol)] = Money(Decimal("100.00"), "USD")
    return prices


class TestRiskAssessmentStubs:
    """Test stubbed risk assessment methods."""

    def test_assess_stock_risk_returns_stub_profile(self):
        """Should return minimal RiskProfile with placeholder values."""
        service = RiskAssessmentService()
        stock = create_test_stock("TEST", 100.00, "A", "Technology")

        risk_profile = service.assess_stock_risk(stock)

        # Should return a RiskProfile with placeholder values
        assert isinstance(risk_profile, RiskProfile)
        assert risk_profile.symbol == stock.symbol
        assert risk_profile.overall_risk_level == RiskLevel.MEDIUM
        assert risk_profile.volatility_risk == RiskLevel.MEDIUM
        assert risk_profile.beta_risk == RiskLevel.MEDIUM
        assert risk_profile.fundamental_risk == RiskLevel.MEDIUM
        assert risk_profile.sector_risk == RiskLevel.MEDIUM
        assert not risk_profile.risk_factors
        assert risk_profile.risk_score == Decimal("50.0")

    def test_assess_portfolio_risk_returns_stub_risk(self):
        """Should return minimal PortfolioRisk with placeholder values."""
        service = RiskAssessmentService()
        portfolio = create_conservative_portfolio()
        prices = create_test_prices(portfolio)

        portfolio_risk = service.assess_portfolio_risk(portfolio, prices)

        # Should return a PortfolioRisk with placeholder values
        assert isinstance(portfolio_risk, PortfolioRisk)
        assert len(portfolio_risk.individual_stock_risks) == len(portfolio)
        assert not portfolio_risk.sector_risks
        assert not portfolio_risk.geographic_risks
        assert not portfolio_risk.correlation_risks
        assert not portfolio_risk.stress_test_results
        assert not portfolio_risk.risk_warnings
        assert not portfolio_risk.mitigation_strategies

    def test_private_methods_removed(self):
        """All private risk assessment methods should be removed."""
        service = RiskAssessmentService()

        # Verify all private methods are removed
        private_methods = [
            "_assess_volatility_risk",
            "_assess_beta_risk",
            "_assess_fundamental_risk",
            "_assess_sector_risk",
            "_calculate_overall_risk_score",
            "_score_to_risk_level",
            "_collect_risk_factors",
            "_calculate_portfolio_risk_metrics",
            "_identify_concentration_risks",
            "_assess_portfolio_sector_risks",
            "_generate_risk_warnings",
            "_suggest_mitigation_strategies",
        ]

        for method_name in private_methods:
            assert not hasattr(
                service, method_name
            ), f"Private method {method_name} should be removed"


class TestRiskAssessmentConfig:
    """Test risk assessment configuration."""

    def test_default_config_creation(self):
        """Should create config with default values."""
        config = RiskAssessmentConfig()

        assert config.var_confidence_level == Decimal("0.95")
        assert config.concentration_threshold == Decimal("0.15")
        assert config.high_volatility_threshold == Decimal("0.30")
        assert config.high_beta_threshold == Decimal("1.5")

    def test_custom_config_creation(self):
        """Should create config with custom values."""
        config = RiskAssessmentConfig(
            var_confidence_level=Decimal("0.99"),
            concentration_threshold=Decimal("0.10"),
            high_volatility_threshold=Decimal("0.25"),
            high_beta_threshold=Decimal("2.0"),
        )

        assert config.var_confidence_level == Decimal("0.99")
        assert config.concentration_threshold == Decimal("0.10")
        assert config.high_volatility_threshold == Decimal("0.25")
        assert config.high_beta_threshold == Decimal("2.0")
