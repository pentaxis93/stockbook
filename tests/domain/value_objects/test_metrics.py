"""
Tests for domain services value objects metrics module.

Comprehensive test coverage for portfolio metrics, risk assessment,
and price analysis value objects with focus on business logic validation.
"""

from decimal import Decimal

from src.domain.value_objects import Money
from src.domain.value_objects.metrics import (
    PortfolioAllocation,
    PortfolioMetrics,
    PositionAllocation,
    PriceAnalysis,
    RiskAssessment,
    RiskLevel,
    TrendDirection,
)
from src.domain.value_objects.stock_symbol import StockSymbol


class TestRiskLevel:
    """Test RiskLevel enumeration."""

    def test_risk_level_values(self) -> None:
        """Test all risk level enum values."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"


class TestTrendDirection:
    """Test TrendDirection enumeration."""

    def test_trend_direction_values(self) -> None:
        """Test all trend direction enum values."""
        assert TrendDirection.UPWARD.value == "upward"
        assert TrendDirection.DOWNWARD.value == "downward"
        assert TrendDirection.SIDEWAYS.value == "sideways"


class TestPositionAllocation:
    """Test PositionAllocation value object."""

    def test_position_allocation_creation(self) -> None:
        """Test creating a valid position allocation."""
        symbol = StockSymbol("AAPL")
        value = Money(Decimal("1000.00"))
        percentage = Decimal("5.0")
        quantity = 10

        allocation = PositionAllocation(
            symbol=symbol,
            value=value,
            percentage=percentage,
            quantity=quantity,
        )

        assert allocation.symbol == symbol
        assert allocation.value == value
        assert allocation.percentage == percentage
        assert allocation.quantity == quantity

    def test_is_overweight_property_false(self) -> None:
        """Test is_overweight property returns False for normal position."""
        allocation = PositionAllocation(
            symbol=StockSymbol("AAPL"),
            value=Money(Decimal("1000.00")),
            percentage=Decimal("5.0"),  # Less than 10%
            quantity=10,
        )

        assert not allocation.is_overweight

    def test_is_overweight_property_true(self) -> None:
        """Test is_overweight property returns True for large position."""
        allocation = PositionAllocation(
            symbol=StockSymbol("AAPL"),
            value=Money(Decimal("2000.00")),
            percentage=Decimal("15.0"),  # Greater than 10%
            quantity=20,
        )

        assert allocation.is_overweight

    def test_is_overweight_property_exactly_ten_percent(self) -> None:
        """Test is_overweight property with exactly 10% allocation."""
        allocation = PositionAllocation(
            symbol=StockSymbol("AAPL"),
            value=Money(Decimal("1000.00")),
            percentage=Decimal("10.0"),  # Exactly 10%
            quantity=10,
        )

        assert not allocation.is_overweight


class TestPortfolioAllocation:
    """Test PortfolioAllocation value object."""

    def test_portfolio_allocation_creation(self) -> None:
        """Test creating a valid portfolio allocation."""
        allocations: dict[str, Decimal] = {
            "Technology": Decimal("40.0"),
            "Healthcare": Decimal("30.0"),
            "Finance": Decimal("30.0"),
        }
        total_value = Money(Decimal("10000.00"))

        portfolio_allocation = PortfolioAllocation(
            allocations=allocations,
            total_value=total_value,
        )

        assert portfolio_allocation.allocations == allocations
        assert portfolio_allocation.total_value == total_value

    def test_get_allocation_percentage_existing_category(self) -> None:
        """Test getting allocation percentage for existing category."""
        allocations: dict[str, Decimal] = {
            "Technology": Decimal("40.0"),
            "Healthcare": Decimal("30.0"),
        }
        portfolio_allocation = PortfolioAllocation(
            allocations=allocations,
            total_value=Money(Decimal("10000.00")),
        )

        percentage = portfolio_allocation.get_allocation_percentage("Technology")

        assert percentage == Decimal("40.0")

    def test_get_allocation_percentage_missing_category(self) -> None:
        """Test getting allocation percentage for non-existent category."""
        allocations: dict[str, Decimal] = {"Technology": Decimal("40.0")}
        portfolio_allocation = PortfolioAllocation(
            allocations=allocations,
            total_value=Money(Decimal("10000.00")),
        )

        percentage = portfolio_allocation.get_allocation_percentage("Energy")

        assert percentage == Decimal("0")


class TestPortfolioMetrics:
    """Test PortfolioMetrics value object."""

    def test_portfolio_metrics_creation(self) -> None:
        """Test creating valid portfolio metrics."""
        position_allocations: list[PositionAllocation] = [
            PositionAllocation(
                symbol=StockSymbol("AAPL"),
                value=Money(Decimal("5000.00")),
                percentage=Decimal("50.0"),
                quantity=50,
            ),
            PositionAllocation(
                symbol=StockSymbol("GOOGL"),
                value=Money(Decimal("3000.00")),
                percentage=Decimal("30.0"),
                quantity=10,
            ),
        ]
        industry_allocation = PortfolioAllocation(
            allocations={"Technology": Decimal("80.0")},
            total_value=Money(Decimal("10000.00")),
        )

        metrics = PortfolioMetrics(
            total_value=Money(Decimal("10000.00")),
            position_count=2,
            position_allocations=position_allocations,
            industry_allocation=industry_allocation,
        )

        assert metrics.total_value == Money(Decimal("10000.00"))
        assert metrics.position_count == 2
        assert metrics.position_allocations == position_allocations
        assert metrics.industry_allocation == industry_allocation

    def test_largest_position_with_positions(self) -> None:
        """Test largest_position property with multiple positions."""
        position_allocations: list[PositionAllocation] = [
            PositionAllocation(
                symbol=StockSymbol("AAPL"),
                value=Money(Decimal("5000.00")),  # Largest
                percentage=Decimal("50.0"),
                quantity=50,
            ),
            PositionAllocation(
                symbol=StockSymbol("GOOGL"),
                value=Money(Decimal("3000.00")),
                percentage=Decimal("30.0"),
                quantity=10,
            ),
        ]
        metrics = PortfolioMetrics(
            total_value=Money(Decimal("10000.00")),
            position_count=2,
            position_allocations=position_allocations,
            industry_allocation=PortfolioAllocation(
                allocations={},
                total_value=Money(Decimal("10000.00")),
            ),
        )

        largest = metrics.largest_position

        assert largest is not None
        assert largest.symbol == StockSymbol("AAPL")
        assert largest.value == Money(Decimal("5000.00"))

    def test_largest_position_with_no_positions(self) -> None:
        """Test largest_position property with empty position list."""
        metrics = PortfolioMetrics(
            total_value=Money(Decimal("0.00")),
            position_count=0,
            position_allocations=[],  # Empty list
            industry_allocation=PortfolioAllocation(
                allocations={},
                total_value=Money(Decimal("0.00")),
            ),
        )

        largest = metrics.largest_position

        assert largest is None

    def test_is_well_diversified_true(self) -> None:
        """Test is_well_diversified property returns True for diversified portfolio."""
        position_allocations: list[PositionAllocation] = [
            PositionAllocation(
                symbol=StockSymbol("AAPL"),
                value=Money(Decimal("1000.00")),
                percentage=Decimal("8.0"),  # Under 10%
                quantity=10,
            ),
            PositionAllocation(
                symbol=StockSymbol("GOOGL"),
                value=Money(Decimal("1000.00")),
                percentage=Decimal("8.0"),  # Under 10%
                quantity=5,
            ),
            PositionAllocation(
                symbol=StockSymbol("MSFT"),
                value=Money(Decimal("1000.00")),
                percentage=Decimal("8.0"),  # Under 10%
                quantity=10,
            ),
            PositionAllocation(
                symbol=StockSymbol("TSLA"),
                value=Money(Decimal("1000.00")),
                percentage=Decimal("8.0"),  # Under 10%
                quantity=5,
            ),
            PositionAllocation(
                symbol=StockSymbol("NVDA"),
                value=Money(Decimal("1000.00")),
                percentage=Decimal("8.0"),  # Under 10%
                quantity=10,
            ),
        ]
        metrics = PortfolioMetrics(
            total_value=Money(Decimal("12500.00")),
            position_count=5,  # >= 5 positions
            position_allocations=position_allocations,
            industry_allocation=PortfolioAllocation(
                allocations={},
                total_value=Money(Decimal("12500.00")),
            ),
        )

        assert metrics.is_well_diversified

    def test_is_well_diversified_false_too_few_positions(self) -> None:
        """Test is_well_diversified property returns False for too few positions."""
        position_allocations: list[PositionAllocation] = [
            PositionAllocation(
                symbol=StockSymbol("AAPL"),
                value=Money(Decimal("3000.00")),
                percentage=Decimal("30.0"),
                quantity=30,
            ),
            PositionAllocation(
                symbol=StockSymbol("GOOGL"),
                value=Money(Decimal("3000.00")),
                percentage=Decimal("30.0"),
                quantity=10,
            ),
        ]
        metrics = PortfolioMetrics(
            total_value=Money(Decimal("10000.00")),
            position_count=2,  # Less than 5 positions
            position_allocations=position_allocations,
            industry_allocation=PortfolioAllocation(
                allocations={},
                total_value=Money(Decimal("10000.00")),
            ),
        )

        assert not metrics.is_well_diversified

    def test_is_well_diversified_false_overweight_position(self) -> None:
        """Test is_well_diversified property returns False for overweight position."""
        position_allocations: list[PositionAllocation] = [
            PositionAllocation(
                symbol=StockSymbol("AAPL"),
                value=Money(Decimal("6000.00")),
                percentage=Decimal("60.0"),  # Overweight (>10%)
                quantity=60,
            ),
            PositionAllocation(
                symbol=StockSymbol("GOOGL"),
                value=Money(Decimal("1000.00")),
                percentage=Decimal("10.0"),
                quantity=5,
            ),
            PositionAllocation(
                symbol=StockSymbol("MSFT"),
                value=Money(Decimal("1000.00")),
                percentage=Decimal("10.0"),
                quantity=10,
            ),
            PositionAllocation(
                symbol=StockSymbol("TSLA"),
                value=Money(Decimal("1000.00")),
                percentage=Decimal("10.0"),
                quantity=5,
            ),
            PositionAllocation(
                symbol=StockSymbol("NVDA"),
                value=Money(Decimal("1000.00")),
                percentage=Decimal("10.0"),
                quantity=10,
            ),
        ]
        metrics = PortfolioMetrics(
            total_value=Money(Decimal("10000.00")),
            position_count=5,  # >= 5 positions
            position_allocations=position_allocations,
            industry_allocation=PortfolioAllocation(
                allocations={},
                total_value=Money(Decimal("10000.00")),
            ),
        )

        assert not metrics.is_well_diversified


class TestRiskAssessment:
    """Test RiskAssessment value object."""

    def test_risk_assessment_creation(self) -> None:
        """Test creating a valid risk assessment."""
        risk_factors: list[str] = ["High volatility", "Market uncertainty"]
        assessment = RiskAssessment(
            overall_risk_level=RiskLevel.MEDIUM,
            risk_score=Decimal("65.0"),
            risk_factors=risk_factors,
        )

        assert assessment.overall_risk_level == RiskLevel.MEDIUM
        assert assessment.risk_score == Decimal("65.0")
        assert assessment.risk_factors == risk_factors

    def test_is_high_risk_true(self) -> None:
        """Test is_high_risk property returns True for high risk assessment."""
        assessment = RiskAssessment(
            overall_risk_level=RiskLevel.HIGH,
            risk_score=Decimal("85.0"),
            risk_factors=["Extreme volatility"],
        )

        assert assessment.is_high_risk

    def test_is_high_risk_false_medium_risk(self) -> None:
        """Test is_high_risk property returns False for medium risk."""
        assessment = RiskAssessment(
            overall_risk_level=RiskLevel.MEDIUM,
            risk_score=Decimal("50.0"),
            risk_factors=["Moderate volatility"],
        )

        assert not assessment.is_high_risk

    def test_is_high_risk_false_low_risk(self) -> None:
        """Test is_high_risk property returns False for low risk."""
        assessment = RiskAssessment(
            overall_risk_level=RiskLevel.LOW,
            risk_score=Decimal("20.0"),
            risk_factors=["Stable fundamentals"],
        )

        assert not assessment.is_high_risk


class TestPriceAnalysis:
    """Test PriceAnalysis value object."""

    def test_price_analysis_creation(self) -> None:
        """Test creating a valid price analysis."""
        symbol = StockSymbol("AAPL")
        current_price = Money(Decimal("150.00"))
        trend_direction = TrendDirection.UPWARD
        volatility_score = Decimal("0.3")

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_direction=trend_direction,
            volatility_score=volatility_score,
        )

        assert analysis.symbol == symbol
        assert analysis.current_price == current_price
        assert analysis.trend_direction == trend_direction
        assert analysis.volatility_score == volatility_score

    def test_is_volatile_true(self) -> None:
        """Test is_volatile property returns True for high volatility."""
        analysis = PriceAnalysis(
            symbol=StockSymbol("TSLA"),
            current_price=Money(Decimal("200.00")),
            trend_direction=TrendDirection.SIDEWAYS,
            volatility_score=Decimal("0.8"),  # >= 0.7
        )

        assert analysis.is_volatile

    def test_is_volatile_false(self) -> None:
        """Test is_volatile property returns False for low volatility."""
        analysis = PriceAnalysis(
            symbol=StockSymbol("AAPL"),
            current_price=Money(Decimal("150.00")),
            trend_direction=TrendDirection.UPWARD,
            volatility_score=Decimal("0.3"),  # < 0.7
        )

        assert not analysis.is_volatile

    def test_is_volatile_exactly_threshold(self) -> None:
        """Test is_volatile property with exactly the threshold value."""
        analysis = PriceAnalysis(
            symbol=StockSymbol("NVDA"),
            current_price=Money(Decimal("400.00")),
            trend_direction=TrendDirection.UPWARD,
            volatility_score=Decimal("0.7"),  # Exactly 0.7
        )

        assert analysis.is_volatile
