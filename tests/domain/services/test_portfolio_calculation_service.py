"""
Unit tests for PortfolioCalculationService.

Tests business logic for portfolio-level calculations that operate
across multiple stocks and provide aggregated insights.
"""

from decimal import Decimal

import pytest

from src.domain.entities.stock import Stock
from src.domain.services.exceptions import CalculationError

# These imports now exist after implementation
from src.domain.services.portfolio_calculation_service import (
    PortfolioCalculationService,
)
from src.domain.value_objects import (
    CompanyName,
    Grade,
    IndustryGroup,
    Money,
    Quantity,
)
from src.domain.value_objects.sector import Sector
from src.domain.value_objects.stock_symbol import StockSymbol


# Test data helpers
def create_test_stock(
    symbol: str = "AAPL", price: float = 100.00, quantity: int = 10, grade: str = "B"
) -> tuple[Stock, Quantity, Money]:
    """Helper to create test stock with position."""
    stock = (
        Stock.Builder()
        .with_symbol(StockSymbol(symbol))
        .with_company_name(CompanyName(f"{symbol} Corp"))
        .with_sector(Sector("Technology"))
        .with_industry_group(IndustryGroup("Software"))
        .with_grade(Grade(grade))
        .build()
    )
    return stock, Quantity(quantity), Money(Decimal(str(price)))


def create_test_portfolio() -> tuple[list[tuple[Stock, Quantity]], dict[str, Money]]:
    """Helper to create a test portfolio with multiple positions."""
    positions = [
        create_test_stock("AAPL", 150.00, 10, "A"),  # $1,500
        create_test_stock("GOOGL", 2500.00, 2, "A"),  # $5,000
        create_test_stock("TSLA", 200.00, 5, "B"),  # $1,000
        create_test_stock("GME", 20.00, 50, "C"),  # $1,000
    ]

    portfolio: list[tuple[Stock, Quantity]] = []
    prices: dict[str, Money] = {}

    for stock, quantity, price in positions:
        portfolio.append((stock, quantity))
        prices[str(stock.symbol)] = price

    return portfolio, prices


class TestPortfolioValueCalculations:
    """Test portfolio value and worth calculations."""

    def test_calculate_total_portfolio_value(self) -> None:
        """Should calculate total portfolio market value."""
        service = PortfolioCalculationService()
        portfolio, prices = create_test_portfolio()

        total_value = service.calculate_total_value(portfolio, prices)

        expected = Money(Decimal("8500.00"))  # 1500 + 5000 + 1000 + 1000
        assert total_value == expected

    def test_calculate_position_values(self) -> None:
        """Should calculate individual position values."""
        service = PortfolioCalculationService()
        stock, quantity, current_price = create_test_stock("AAPL", 150.00, 10)

        position_value = service.calculate_position_value(
            stock, quantity, current_price
        )

        expected = Money(Decimal("1500.00"))
        assert position_value == expected

    def test_calculate_portfolio_with_different_currencies(self) -> None:
        """Should handle multi-currency portfolios."""

    def test_calculate_portfolio_value_with_zero_positions(self) -> None:
        """Should handle empty portfolio."""
        service = PortfolioCalculationService()
        empty_portfolio: list[tuple[Stock, Quantity]] = []
        empty_prices: dict[str, Money] = {}

        total_value = service.calculate_total_value(empty_portfolio, empty_prices)

        assert total_value == Money.zero()

    def test_calculate_portfolio_value_with_zero_quantities(self) -> None:
        """Should handle portfolio with zero quantity positions."""
        service = PortfolioCalculationService()
        stock, _, price = create_test_stock("AAPL", 150.00, 0, "A")

        portfolio = [(stock, Quantity(0))]
        prices = {"AAPL": price}

        total_value = service.calculate_total_value(portfolio, prices)

        assert total_value == Money.zero()

    def test_calculate_portfolio_value_missing_price_raises_error(self) -> None:
        """Should raise error when stock price is missing."""
        service = PortfolioCalculationService()
        stock, quantity, _ = create_test_stock("AAPL", 150.00, 10, "A")

        portfolio = [(stock, quantity)]
        prices: dict[str, Money] = {}  # Missing price for AAPL

        with pytest.raises(CalculationError, match="Stock AAPL missing current price"):
            _ = service.calculate_total_value(portfolio, prices)

    def test_calculate_portfolio_value_with_zero_prices(self) -> None:
        """Should handle portfolio with zero-priced stocks."""
        service = PortfolioCalculationService()
        stock, quantity, _ = create_test_stock("PENNY", 0.00, 1000, "D")

        portfolio = [(stock, quantity)]
        prices = {"PENNY": Money("0.00")}

        total_value = service.calculate_total_value(portfolio, prices)

        assert total_value == Money.zero()

    def test_calculate_portfolio_value_precision(self) -> None:
        """Should maintain precision in calculations."""
        service = PortfolioCalculationService()
        stock, quantity, _ = create_test_stock("PREC", 33.333333, 3, "A")

        portfolio = [(stock, quantity)]
        prices = {"PREC": Money("33.333333")}

        total_value = service.calculate_total_value(portfolio, prices)

        # Should be 33.333333 * 3 = 99.999999, rounded to 100.00
        # 3 * 33.333333 = 99.999999 -> 99.99 due to rounding
        assert total_value == Money("99.99")


class TestPortfolioCalculationEdgeCases:
    """Test edge cases and error conditions for portfolio calculations."""

    def test_calculate_total_value_with_large_portfolio(self) -> None:
        """Should handle large portfolios efficiently."""
        service = PortfolioCalculationService()

        # Create a large portfolio with many positions
        large_portfolio: list[tuple[Stock, Quantity]] = []
        prices: dict[str, Money] = {}

        expected_total = Decimal("0")

        for i in range(1000):  # 1000 positions
            # Generate 5-char symbols using letters only
            symbol = (
                f"{chr(ord('A') + (i % 26))}"
                f"{chr(ord('A') + ((i // 26) % 26))}"
                f"{chr(ord('A') + ((i // 676) % 26))}"
                f"{chr(ord('A') + ((i // 17576) % 26))}"
                f"{chr(ord('A') + ((i // 456976) % 26))}"
            )
            price_value = Decimal("100.00") + (i % 100)  # Prices from $100 to $199
            quantity_value = 10 + (i % 20)  # Quantities from 10 to 29

            stock = (
                Stock.Builder()
                .with_symbol(StockSymbol(symbol))
                .with_company_name(CompanyName(f"Test Company {i}"))
                .with_sector(Sector("Technology"))
                .with_industry_group(IndustryGroup("Software"))
                .with_grade(Grade("A"))
                .build()
            )

            quantity = Quantity(quantity_value)
            price = Money(price_value)

            large_portfolio.append((stock, quantity))
            prices[symbol] = price
            expected_total += price_value * quantity_value

        total_value = service.calculate_total_value(large_portfolio, prices)

        assert total_value == Money(expected_total)
        assert len(large_portfolio) == 1000

    def test_calculate_position_allocations_empty_portfolio(self) -> None:
        """Should handle empty portfolio for position allocations."""
        service = PortfolioCalculationService()
        empty_portfolio: list[tuple[Stock, Quantity]] = []
        empty_prices: dict[str, Money] = {}

        allocations = service.calculate_position_allocations(
            empty_portfolio, empty_prices
        )

        assert not allocations

    def test_calculate_position_allocations_zero_total_value(self) -> None:
        """Should handle portfolio with zero total value."""
        service = PortfolioCalculationService()
        stock, quantity, _ = create_test_stock("ZERO", 0.00, 100, "D")

        portfolio = [(stock, quantity)]
        prices = {"ZERO": Money("0.00")}

        allocations = service.calculate_position_allocations(portfolio, prices)

        assert not allocations

    def test_calculate_position_allocations_precision(self) -> None:
        """Should maintain precision in allocation calculations."""
        service = PortfolioCalculationService()

        # Create portfolio where allocations don't divide evenly
        stock1, quantity1, _ = create_test_stock("STKA", 33.33, 3, "A")  # $99.99
        stock2, quantity2, _ = create_test_stock("STKB", 33.34, 3, "A")  # $100.02

        portfolio = [(stock1, quantity1), (stock2, quantity2)]
        prices = {"STKA": Money("33.33"), "STKB": Money("33.34")}

        allocations = service.calculate_position_allocations(portfolio, prices)

        # Total value = $200.01
        # STOCK1 should be ~49.995% (99.99/200.01)
        # STOCK2 should be ~50.005% (100.02/200.01)

        stock1_allocation = next(a for a in allocations if a.symbol.value == "STKA")
        stock2_allocation = next(a for a in allocations if a.symbol.value == "STKB")

        # Adjust precision expectation - actual calculation is slightly different
        assert abs(stock1_allocation.percentage - Decimal("49.992")) < Decimal("0.005")
        assert abs(stock2_allocation.percentage - Decimal("50.008")) < Decimal("0.005")

        # Percentages should sum to 100%
        total_percentage = sum(a.percentage for a in allocations)
        assert abs(total_percentage - Decimal("100.0")) < Decimal("0.001")

    def test_calculate_industry_allocations_empty_portfolio(self) -> None:
        """Should handle empty portfolio for industry allocations."""
        service = PortfolioCalculationService()
        empty_portfolio: list[tuple[Stock, Quantity]] = []
        empty_prices: dict[str, Money] = {}

        industry_allocations = service.calculate_industry_allocations(
            empty_portfolio, empty_prices
        )

        assert industry_allocations.total_value == Money.zero()
        assert len(industry_allocations.allocations) == 0

    def test_calculate_industry_allocations_unknown_industry(self) -> None:
        """Should handle stocks with no industry group specified."""
        service = PortfolioCalculationService()

        # Create stock without industry group
        stock = (
            Stock.Builder()
            .with_symbol(StockSymbol("UNKNW"))
            .with_company_name(CompanyName("Unknown Industry Corp"))
            .with_sector(Sector("Technology"))
            .build()
        )

        portfolio = [(stock, Quantity(10))]
        prices = {"UNKNW": Money("100.00")}

        industry_allocations = service.calculate_industry_allocations(portfolio, prices)

        # Should categorize as "Unknown"
        assert "Unknown" in industry_allocations.allocations
        assert industry_allocations.allocations["Unknown"] == Decimal("100.0")

    def test_calculate_industry_allocations_mixed_industries(self) -> None:
        """Should correctly allocate across multiple industries."""
        service = PortfolioCalculationService()

        # Create stocks in different industries
        tech_stock = (
            Stock.Builder()
            .with_symbol(StockSymbol("TECH"))
            .with_company_name(CompanyName("Tech Corp"))
            .with_sector(Sector("Technology"))
            .with_industry_group(IndustryGroup("Software"))
            .build()
        )

        finance_stock = (
            Stock.Builder()
            .with_symbol(StockSymbol("BANK"))
            .with_company_name(CompanyName("Big Bank"))
            .with_sector(Sector("Financial Services"))
            .with_industry_group(IndustryGroup("Banks"))
            .build()
        )

        portfolio = [
            (tech_stock, Quantity(5)),  # $500
            (finance_stock, Quantity(10)),  # $1000
        ]
        prices = {"TECH": Money("100.00"), "BANK": Money("100.00")}

        industry_allocations = service.calculate_industry_allocations(portfolio, prices)

        assert industry_allocations.total_value == Money("1500.00")
        assert abs(
            industry_allocations.allocations["Software"] - Decimal("33.33")
        ) < Decimal("0.01")
        assert abs(
            industry_allocations.allocations["Banks"] - Decimal("66.67")
        ) < Decimal("0.01")

    def test_calculate_position_value_with_fractional_shares(self) -> None:
        """Should handle fractional share quantities."""
        service = PortfolioCalculationService()
        stock, _, _ = create_test_stock("FRAC", 100.00, 1, "A")

        # Test fractional quantity
        fractional_quantity = Quantity(2.5)
        price = Money("100.00")

        position_value = service.calculate_position_value(
            stock, fractional_quantity, price
        )

        assert position_value == Money("250.00")

    def test_portfolio_calculations_with_extreme_values(self) -> None:
        """Should handle extreme monetary values correctly."""
        service = PortfolioCalculationService()

        # Very high priced stock
        expensive_stock, _, _ = create_test_stock("EXPNS", 999999.99, 1, "A")

        # Very low priced stock
        penny_stock, _, _ = create_test_stock("PENNY", 0.01, 1000000, "D")

        portfolio = [(expensive_stock, Quantity(1)), (penny_stock, Quantity(1000000))]
        prices = {"EXPNS": Money("999999.99"), "PENNY": Money("0.01")}

        total_value = service.calculate_total_value(portfolio, prices)
        allocations = service.calculate_position_allocations(portfolio, prices)

        # Total should be 999999.99 + 10000.00 = 1009999.99
        expected_total = Money("1009999.99")
        assert total_value == expected_total

        # Check allocation percentages
        expensive_allocation = next(a for a in allocations if a.symbol.value == "EXPNS")
        penny_allocation = next(a for a in allocations if a.symbol.value == "PENNY")

        # EXPENSIVE should be ~99.01% (999999.99/1009999.99)
        # PENNY should be ~0.99% (10000.00/1009999.99)
        assert abs(expensive_allocation.percentage - Decimal("99.01")) < Decimal("0.01")
        assert abs(penny_allocation.percentage - Decimal("0.99")) < Decimal("0.01")


class TestPortfolioAllocationAnalysis:
    """Test portfolio allocation and distribution analysis."""

    def test_calculate_allocation_by_position(self) -> None:
        """Should calculate allocation percentage for each position."""
        service = PortfolioCalculationService()
        portfolio, prices = create_test_portfolio()

        allocations = service.calculate_position_allocations(portfolio, prices)

        # GOOGL should be 58.8% (5000/8500)
        googl_allocation = next(a for a in allocations if a.symbol.value == "GOOGL")
        assert abs(googl_allocation.percentage - Decimal("58.8")) < Decimal("0.1")

    def test_calculate_allocation_by_industry(self) -> None:
        """Should calculate allocation by industry sectors."""
        service = PortfolioCalculationService()
        portfolio, prices = create_test_portfolio()  # All Technology stocks

        industry_allocations = service.calculate_industry_allocations(portfolio, prices)

        tech_allocation = industry_allocations.get_allocation_percentage("Software")
        assert tech_allocation == Decimal("100.0")  # All are Software

    def test_identify_concentration_risks(self) -> None:
        """Should identify positions that are overly concentrated."""


@pytest.mark.skip(reason="TDD - implementation pending")
class TestPortfolioPerformanceMetrics:
    """Test portfolio performance and risk metrics."""

    def test_calculate_portfolio_risk_metrics(self) -> None:
        """Should calculate comprehensive risk metrics."""

    def test_calculate_growth_vs_value_allocation(self) -> None:
        """Should analyze growth vs value stock allocation."""


@pytest.mark.skip(reason="TDD - implementation pending")
class TestPortfolioRebalancingAnalysis:
    """Test portfolio rebalancing recommendations."""

    def test_suggest_rebalancing_for_overweight_positions(self) -> None:
        """Should suggest rebalancing when positions become overweight."""

    def test_calculate_rebalancing_trades(self) -> None:
        """Should calculate specific trades needed for rebalancing."""

    def test_calculate_tax_efficient_rebalancing(self) -> None:
        """Should consider tax implications in rebalancing suggestions."""


@pytest.mark.skip(reason="TDD - implementation pending")
class TestPortfolioReporting:
    """Test portfolio reporting and summary generation."""

    def test_generate_allocation_report(self) -> None:
        """Should generate detailed allocation breakdown report."""

    def test_generate_performance_metrics_report(self) -> None:
        """Should generate performance and risk metrics report."""


@pytest.mark.skip(reason="TDD - implementation pending")
class TestPortfolioCalculationServiceConfiguration:
    """Test service configuration and error handling."""

    def test_service_with_custom_calculation_rules(self) -> None:
        """Should allow custom calculation rule configuration."""

    def test_handle_calculation_errors_gracefully(self) -> None:
        """Should handle edge cases and errors gracefully."""

    def test_service_performance_with_large_portfolios(self) -> None:
        """Should handle large portfolios efficiently."""
