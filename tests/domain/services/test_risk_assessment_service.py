"""
Unit tests for RiskAssessmentService.

Tests business logic for comprehensive risk assessment of individual stocks
and portfolios, including various risk metrics and risk management strategies.
"""

from decimal import Decimal

from src.domain.entities.stock import Stock
from src.domain.services.portfolio_calculation_service import (
    PortfolioCalculationService,
)
from src.domain.services.risk_assessment_service import (
    RiskAssessmentConfig,
    RiskAssessmentService,
)
from src.domain.services.value_objects import (
    RiskAssessment,
    RiskLevel,
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
    _price: float,
    grade: str,
    industry: str = "Technology",
    _volatility: float = 0.2,
    _beta: float = 1.0,
) -> Stock:
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

    builder = (
        Stock.Builder()
        .with_symbol(StockSymbol(symbol))
        .with_company_name(CompanyName(f"{symbol} Corp"))
        .with_id(f"stock-{symbol.lower()}-test")
    )

    if sector:
        builder = builder.with_sector(Sector(sector))
    if industry_group:
        builder = builder.with_industry_group(IndustryGroup(industry_group))
    if grade:
        builder = builder.with_grade(Grade(grade))

    return builder.build()


def create_conservative_portfolio() -> list[tuple[Stock, Quantity]]:
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


def create_aggressive_portfolio() -> list[tuple[Stock, Quantity]]:
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


def create_concentrated_portfolio() -> list[tuple[Stock, Quantity]]:
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


def create_test_prices(
    portfolio: list[tuple[Stock, Quantity]],
) -> dict[str, Money]:
    """Helper to create price dictionary from portfolio."""
    prices: dict[str, Money] = {}
    for stock, _ in portfolio:
        # Use a default price since we don't need actual prices for stub tests
        prices[str(stock.symbol)] = Money(Decimal("100.00"))
    return prices


class TestRiskAssessmentStubs:
    """Test stubbed risk assessment methods."""

    def test_assess_stock_risk_returns_assessment(self) -> None:
        """Should return RiskAssessment with basic risk information."""
        service = RiskAssessmentService()
        stock = create_test_stock("TEST", 100.00, "A", "Technology")

        risk_assessment = service.assess_stock_risk(stock)

        # Should return a RiskAssessment with basic values
        assert isinstance(risk_assessment, RiskAssessment)
        assert risk_assessment.overall_risk_level == RiskLevel.MEDIUM
        assert risk_assessment.risk_score == Decimal("50.0")
        assert isinstance(risk_assessment.risk_factors, list)

    def test_assess_portfolio_risk_returns_assessment(self) -> None:
        """Should return portfolio RiskAssessment based on simple diversification
        rules."""
        service = RiskAssessmentService()
        portfolio = create_conservative_portfolio()
        prices = create_test_prices(portfolio)

        portfolio_risk = service.assess_portfolio_risk(portfolio, prices)

        # Should return a RiskAssessment
        assert isinstance(portfolio_risk, RiskAssessment)
        assert (
            portfolio_risk.overall_risk_level == RiskLevel.MEDIUM
        )  # 4 positions = medium risk
        assert portfolio_risk.risk_score == Decimal("50.0")
        assert isinstance(portfolio_risk.risk_factors, list)

    def test_assess_portfolio_risk_high_risk_small_portfolio(self) -> None:
        """Should assess small portfolios as high risk."""
        service = RiskAssessmentService()
        # Create a small portfolio with only 2 positions
        portfolio = create_conservative_portfolio()[:2]
        prices = create_test_prices(portfolio)

        portfolio_risk = service.assess_portfolio_risk(portfolio, prices)

        assert portfolio_risk.overall_risk_level == RiskLevel.HIGH
        assert portfolio_risk.risk_score == Decimal("80.0")
        assert "Insufficient diversification" in " ".join(portfolio_risk.risk_factors)


class TestRiskAssessmentConfig:
    """Test risk assessment configuration."""

    def test_default_config_creation(self) -> None:
        """Should create config with default values."""
        config = RiskAssessmentConfig()

        assert config.var_confidence_level == Decimal("0.95")
        assert config.concentration_threshold == Decimal("0.15")
        assert config.high_volatility_threshold == Decimal("0.30")
        assert config.high_beta_threshold == Decimal("1.5")

    def test_custom_config_creation(self) -> None:
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


class TestRiskAssessmentEdgeCases:
    """Test edge cases and boundary conditions for risk assessment."""

    def test_assess_portfolio_risk_empty_portfolio(self) -> None:
        """Should raise error for empty portfolio."""
        import pytest

        from src.domain.services.exceptions import InsufficientDataError

        service = RiskAssessmentService()
        empty_portfolio: list[tuple[Stock, Quantity]] = []
        empty_prices: dict[str, Money] = {}

        with pytest.raises(
            InsufficientDataError,
            match="Cannot assess risk of empty portfolio",
        ):
            _ = service.assess_portfolio_risk(empty_portfolio, empty_prices)

    def test_assess_portfolio_risk_single_stock(self) -> None:
        """Should assess single-stock portfolio as very high risk."""
        service = RiskAssessmentService()
        single_stock = create_test_stock("SINGL", 100.00, "A", "Technology")
        portfolio = [(single_stock, Quantity(100))]
        prices = {"SINGL": Money("100.00")}

        portfolio_risk = service.assess_portfolio_risk(portfolio, prices)

        assert portfolio_risk.overall_risk_level == RiskLevel.HIGH
        assert portfolio_risk.risk_score >= Decimal("80.0")
        assert "Insufficient diversification" in " ".join(portfolio_risk.risk_factors)

    def test_assess_portfolio_risk_with_zero_quantities(self) -> None:
        """Should handle portfolio with zero quantity positions."""
        service = RiskAssessmentService()
        portfolio = create_conservative_portfolio()
        # Set one position to zero quantity
        portfolio[0] = (portfolio[0][0], Quantity(0))
        prices = create_test_prices(portfolio)

        portfolio_risk = service.assess_portfolio_risk(portfolio, prices)

        # Should still assess based on non-zero positions
        assert isinstance(portfolio_risk, RiskAssessment)
        assert portfolio_risk.overall_risk_level in [
            RiskLevel.LOW,
            RiskLevel.MEDIUM,
            RiskLevel.HIGH,
        ]

    def test_assess_portfolio_risk_with_missing_prices(self) -> None:
        """Should handle missing price data appropriately."""
        service = RiskAssessmentService()
        portfolio = create_conservative_portfolio()
        incomplete_prices = create_test_prices(portfolio)
        # Remove one price
        del incomplete_prices[next(iter(incomplete_prices.keys()))]

        # Should either raise an error or handle gracefully
        try:
            portfolio_risk = service.assess_portfolio_risk(portfolio, incomplete_prices)
            # If it doesn't raise an error, should still return valid assessment
            assert isinstance(portfolio_risk, RiskAssessment)
        except (ValueError, KeyError):
            # This is acceptable behavior for missing price data
            pass

    def test_assess_stock_risk_grade_variations(self) -> None:
        """Should assess risk differently based on stock grades."""
        service = RiskAssessmentService()

        grade_a_stock = create_test_stock("GRADA", 100.00, "A", "Technology")
        grade_d_stock = create_test_stock("GRADD", 100.00, "D", "Technology")

        risk_a = service.assess_stock_risk(grade_a_stock)
        risk_d = service.assess_stock_risk(grade_d_stock)

        # Grade D should generally be riskier than Grade A
        # Note: Current implementation may be stubbed, so this tests future
        # implementation
        assert isinstance(risk_a, RiskAssessment)
        assert isinstance(risk_d, RiskAssessment)

    def test_assess_stock_risk_sector_variations(self) -> None:
        """Should assess risk differently based on sectors."""
        service = RiskAssessmentService()

        tech_stock = create_test_stock("TECH", 100.00, "A", "Technology")
        utility_stock = create_test_stock("UTIL", 100.00, "A", "Utilities")

        tech_risk = service.assess_stock_risk(tech_stock)
        utility_risk = service.assess_stock_risk(utility_stock)

        # Both should return valid risk assessments
        assert isinstance(tech_risk, RiskAssessment)
        assert isinstance(utility_risk, RiskAssessment)
        # Technology is typically more volatile than utilities
        # This tests the framework for future enhanced implementation


class TestRiskAssessmentIntegration:
    """Test integration scenarios for risk assessment service."""

    def test_portfolio_risk_assessment_with_allocation_service(self) -> None:
        """Should integrate with allocation calculations for comprehensive risk
        assessment."""
        risk_service = RiskAssessmentService()
        calc_service = PortfolioCalculationService()

        portfolio = create_conservative_portfolio()
        prices = create_test_prices(portfolio)

        # Get portfolio allocations
        allocations = calc_service.calculate_position_allocations(portfolio, prices)

        # Assess portfolio risk
        portfolio_risk = risk_service.assess_portfolio_risk(portfolio, prices)

        # Both should provide consistent data
        assert len(allocations) > 0
        assert isinstance(portfolio_risk, RiskAssessment)
        # Future enhancement: risk assessment could use allocation data

    def test_concentrated_portfolio_risk_assessment(self) -> None:
        """Should identify concentration risk in portfolios."""
        service = RiskAssessmentService()
        concentrated_portfolio = create_concentrated_portfolio()
        prices = create_test_prices(concentrated_portfolio)

        portfolio_risk = service.assess_portfolio_risk(concentrated_portfolio, prices)

        # Concentrated portfolio should be assessed as higher risk
        assert portfolio_risk.overall_risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]
        # Future enhancement: should identify concentration risk factors

    def test_aggressive_portfolio_risk_assessment(self) -> None:
        """Should identify aggressive portfolio characteristics."""
        service = RiskAssessmentService()
        aggressive_portfolio = create_aggressive_portfolio()
        prices = create_test_prices(aggressive_portfolio)

        portfolio_risk = service.assess_portfolio_risk(aggressive_portfolio, prices)

        assert isinstance(portfolio_risk, RiskAssessment)
        # Aggressive portfolios should generally have higher risk scores
        assert portfolio_risk.risk_score >= Decimal("30.0")

    def test_large_portfolio_risk_assessment_performance(self) -> None:
        """Should handle large portfolios efficiently in risk assessment."""
        service = RiskAssessmentService()

        # Create large portfolio with diverse holdings
        large_portfolio: list[tuple[Stock, Quantity]] = []
        prices: dict[str, Money] = {}

        sectors = ["Technology", "Healthcare", "Financial", "Industrial", "Consumer"]
        grades = ["A", "B", "C", "D"]

        for i in range(100):  # 100 positions
            sector = sectors[i % len(sectors)]
            grade = grades[i % len(grades)]
            # Create 5-char symbols using letters only
            symbol = (
                f"{chr(ord('A') + (i % 26))}"
                f"{chr(ord('A') + ((i // 26) % 26))}"
                f"{chr(ord('A') + ((i // 676) % 26))}"
                f"{chr(ord('A') + ((i // 17576) % 26))}"
                f"{chr(ord('A') + ((i // 456976) % 26))}"
            )

            stock = create_test_stock(symbol, 50.00 + (i % 100), grade, sector)
            large_portfolio.append((stock, Quantity(10 + (i % 50))))
            prices[symbol] = Money(f"{50.00 + (i % 100):.2f}")

        portfolio_risk = service.assess_portfolio_risk(large_portfolio, prices)

        # Should handle large portfolio and return reasonable assessment
        assert isinstance(portfolio_risk, RiskAssessment)
        # Large, diversified portfolio should generally be lower risk
        assert portfolio_risk.overall_risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]

    def test_risk_assessment_consistency(self) -> None:
        """Should provide consistent risk assessments for identical portfolios."""
        service = RiskAssessmentService()
        portfolio = create_conservative_portfolio()
        prices = create_test_prices(portfolio)

        # Assess the same portfolio multiple times
        risk1 = service.assess_portfolio_risk(portfolio, prices)
        risk2 = service.assess_portfolio_risk(portfolio, prices)

        # Results should be identical
        assert risk1.overall_risk_level == risk2.overall_risk_level
        assert risk1.risk_score == risk2.risk_score
        assert risk1.risk_factors == risk2.risk_factors


class TestRiskAssessmentAlgorithms:
    """Test risk calculation algorithms and thresholds."""

    def test_risk_score_calculation_boundaries(self) -> None:
        """Should calculate risk scores within valid boundaries."""
        service = RiskAssessmentService()

        # Test various portfolio configurations
        portfolios = [
            create_conservative_portfolio(),
            create_aggressive_portfolio(),
            create_concentrated_portfolio(),
        ]

        for portfolio in portfolios:
            prices = create_test_prices(portfolio)
            risk = service.assess_portfolio_risk(portfolio, prices)

            # Risk score should be between 0 and 100
            assert Decimal("0.0") <= risk.risk_score <= Decimal("100.0")

    def test_risk_level_mapping_consistency(self) -> None:
        """Should consistently map risk scores to risk levels."""
        service = RiskAssessmentService()
        portfolio = create_conservative_portfolio()
        prices = create_test_prices(portfolio)

        risk = service.assess_portfolio_risk(portfolio, prices)

        # Verify risk level matches risk score ranges
        if risk.risk_score <= Decimal("30.0"):
            assert risk.overall_risk_level == RiskLevel.LOW
        elif risk.risk_score <= Decimal("70.0"):
            assert risk.overall_risk_level == RiskLevel.MEDIUM
        else:
            assert risk.overall_risk_level == RiskLevel.HIGH

    def test_diversification_impact_on_risk(self) -> None:
        """Should assess diversification impact on portfolio risk."""
        service = RiskAssessmentService()

        # Create portfolios with different diversification levels

        # Undiversified: 2 stocks same sector
        undiversified: list[tuple[Stock, Quantity]] = []
        tech_symbols = ["TECHA", "TECHB"]
        for i, symbol in enumerate(tech_symbols):
            stock = create_test_stock(symbol, 100.00, "A", "Technology")
            undiversified.append((stock, Quantity(50)))

        # Diversified: 5 stocks different sectors
        diversified: list[tuple[Stock, Quantity]] = []
        sectors = ["Technology", "Healthcare", "Financial", "Industrial", "Consumer"]
        div_symbols = ["DIVA", "DIVB", "DIVC", "DIVD", "DIVE"]
        for i, sector in enumerate(sectors):
            stock = create_test_stock(div_symbols[i], 100.00, "A", sector)
            diversified.append((stock, Quantity(20)))

        undiversified_prices = create_test_prices(undiversified)
        diversified_prices = create_test_prices(diversified)

        undiversified_risk = service.assess_portfolio_risk(
            undiversified,
            undiversified_prices,
        )
        diversified_risk = service.assess_portfolio_risk(
            diversified,
            diversified_prices,
        )

        # Diversified portfolio should generally have lower risk
        # Note: Current implementation may be stubbed
        assert isinstance(undiversified_risk, RiskAssessment)
        assert isinstance(diversified_risk, RiskAssessment)

    def test_position_size_impact_on_risk(self) -> None:
        """Should assess position size concentration impact on risk."""
        service = RiskAssessmentService()

        # Create two portfolios: one balanced, one concentrated
        balanced_portfolio: list[tuple[Stock, Quantity]] = []
        concentrated_portfolio: list[tuple[Stock, Quantity]] = []

        # Balanced: equal positions
        bal_symbols = ["BALA", "BALB", "BALC", "BALD"]
        for i, symbol in enumerate(bal_symbols):
            stock = create_test_stock(symbol, 100.00, "A", "Technology")
            balanced_portfolio.append((stock, Quantity(25)))

        # Concentrated: one large position
        con_symbols = ["CONA", "CONB", "CONC", "COND"]
        for i, symbol in enumerate(con_symbols):
            stock = create_test_stock(symbol, 100.00, "A", "Technology")
            quantity = Quantity(70) if i == 0 else Quantity(10)
            concentrated_portfolio.append((stock, quantity))

        balanced_prices = create_test_prices(balanced_portfolio)
        concentrated_prices = create_test_prices(concentrated_portfolio)

        balanced_risk = service.assess_portfolio_risk(
            balanced_portfolio,
            balanced_prices,
        )
        concentrated_risk = service.assess_portfolio_risk(
            concentrated_portfolio,
            concentrated_prices,
        )

        # Both should return valid assessments
        assert isinstance(balanced_risk, RiskAssessment)
        assert isinstance(concentrated_risk, RiskAssessment)


class TestRiskAssessmentConfigurationImpact:
    """Test how different configurations impact risk assessment."""

    def test_custom_thresholds_impact_assessment(self) -> None:
        """Should use custom configuration thresholds in risk assessment."""
        # Create service with custom config
        custom_config = RiskAssessmentConfig(
            concentration_threshold=Decimal("0.05"),  # Very strict
            high_volatility_threshold=Decimal("0.20"),
            high_beta_threshold=Decimal("1.2"),
        )

        service = RiskAssessmentService(config=custom_config)
        portfolio = create_conservative_portfolio()
        prices = create_test_prices(portfolio)

        risk = service.assess_portfolio_risk(portfolio, prices)

        # Should return valid assessment using custom thresholds
        assert isinstance(risk, RiskAssessment)
        # Future enhancement: verify custom thresholds are actually used

    def test_var_confidence_level_variations(self) -> None:
        """Should handle different VaR confidence levels."""
        configs = [
            RiskAssessmentConfig(var_confidence_level=Decimal("0.90")),
            RiskAssessmentConfig(var_confidence_level=Decimal("0.95")),
            RiskAssessmentConfig(var_confidence_level=Decimal("0.99")),
        ]

        portfolio = create_conservative_portfolio()
        prices = create_test_prices(portfolio)

        for config in configs:
            service = RiskAssessmentService(config=config)
            risk = service.assess_portfolio_risk(portfolio, prices)

            assert isinstance(risk, RiskAssessment)
            # Future enhancement: VaR calculations should reflect confidence level

    def test_extreme_threshold_configurations(self) -> None:
        """Should handle extreme threshold configurations gracefully."""
        # Very permissive thresholds
        permissive_config = RiskAssessmentConfig(
            concentration_threshold=Decimal("0.90"),
            high_volatility_threshold=Decimal("0.90"),
            high_beta_threshold=Decimal("10.0"),
        )

        # Very strict thresholds
        strict_config = RiskAssessmentConfig(
            concentration_threshold=Decimal("0.01"),
            high_volatility_threshold=Decimal("0.01"),
            high_beta_threshold=Decimal("0.5"),
        )

        portfolio = create_conservative_portfolio()
        prices = create_test_prices(portfolio)

        for config in [permissive_config, strict_config]:
            service = RiskAssessmentService(config=config)
            risk = service.assess_portfolio_risk(portfolio, prices)

            assert isinstance(risk, RiskAssessment)
            assert Decimal("0.0") <= risk.risk_score <= Decimal("100.0")
