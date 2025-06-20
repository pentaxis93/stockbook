"""
Portfolio calculation service.

Provides business logic for portfolio-level calculations that operate
across multiple stocks and provide aggregated insights.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from shared_kernel.value_objects import Money, Quantity
from src.domain.entities.stock_entity import StockEntity

from .exceptions import CalculationError
from .value_objects.portfolio_metrics import (
    PortfolioAllocation,
    PortfolioSummary,
    PositionAllocation,
)


class PortfolioCalculationConfig:
    """Configuration for portfolio calculation rules."""

    def __init__(
        self,
        concentration_threshold: Decimal = Decimal("0.15"),  # 15% max per position
        minimum_diversification_score: Decimal = Decimal("0.6"),
        default_currency: str = "USD",
    ):
        self.concentration_threshold = concentration_threshold
        self.minimum_diversification_score = minimum_diversification_score
        self.default_currency = default_currency


class PortfolioCalculationService:
    """
    Service for portfolio-level calculations and analysis.

    Handles calculations that operate across multiple stocks and provide
    aggregated portfolio insights and metrics.
    """

    def __init__(self, config: Optional[PortfolioCalculationConfig] = None):
        self.config = config or PortfolioCalculationConfig()

    def calculate_total_value(
        self, portfolio: List[Tuple[StockEntity, Quantity]], prices: Dict[str, Money]
    ) -> Money:
        """Calculate total portfolio market value."""
        if not portfolio:
            return Money.zero(self.config.default_currency)

        total_amount = Decimal("0")
        currency = None

        for stock, quantity in portfolio:
            symbol_str = str(stock.symbol)
            if symbol_str not in prices:
                raise CalculationError(
                    f"Stock {stock.symbol} missing current price",
                    calculation_type="total_value",
                    input_data={"symbol": symbol_str},
                )

            current_price = prices[symbol_str]
            position_value = current_price.amount * Decimal(str(quantity.value))
            total_amount += position_value

            # Use the currency from the first stock
            if currency is None:
                currency = current_price.currency
            elif currency != current_price.currency:
                raise CalculationError(
                    "Multi-currency portfolios require currency conversion",
                    calculation_type="total_value",
                )

        return Money(total_amount, currency or self.config.default_currency)

    def calculate_position_value(
        self, _stock: StockEntity, quantity: Quantity, current_price: Money
    ) -> Money:
        """Calculate individual position value."""
        return Money(
            current_price.amount * Decimal(str(quantity.value)), current_price.currency
        )

    def calculate_position_allocations(
        self, portfolio: List[Tuple[StockEntity, Quantity]], prices: Dict[str, Money]
    ) -> List[PositionAllocation]:
        """Calculate allocation percentage for each position."""
        if not portfolio:
            return []

        total_value = self.calculate_total_value(portfolio, prices)
        if total_value.amount == 0:
            return []

        allocations = []
        for stock, quantity in portfolio:
            symbol_str = str(stock.symbol)
            current_price = prices[symbol_str]
            position_value = self.calculate_position_value(
                stock, quantity, current_price
            )
            percentage = (position_value.amount / total_value.amount) * Decimal("100")

            allocation = PositionAllocation(
                symbol=stock.symbol,
                value=position_value,
                percentage=percentage,
                quantity=int(quantity.value),
            )
            allocations.append(allocation)

        return allocations

    def calculate_industry_allocations(
        self, portfolio: List[Tuple[StockEntity, Quantity]], prices: Dict[str, Money]
    ) -> PortfolioAllocation:
        """Calculate allocation by industry sectors."""
        if not portfolio:
            return PortfolioAllocation({}, Money.zero(self.config.default_currency))

        total_value = self.calculate_total_value(portfolio, prices)
        industry_values: Dict[str, Decimal] = {}

        for stock, quantity in portfolio:
            industry = stock.industry_group.value if stock.industry_group else "Unknown"
            symbol_str = str(stock.symbol)
            current_price = prices[symbol_str]
            position_value = self.calculate_position_value(
                stock, quantity, current_price
            )

            if industry not in industry_values:
                industry_values[industry] = Decimal("0")
            industry_values[industry] += position_value.amount

        # Convert to percentages
        industry_percentages = {}
        for industry, value in industry_values.items():
            percentage = (
                (value / total_value.amount) * Decimal("100")
                if total_value.amount > 0
                else Decimal("0")
            )
            industry_percentages[industry] = percentage

        return PortfolioAllocation(industry_percentages, total_value)

    def calculate_grade_allocations(
        self, portfolio: List[Tuple[StockEntity, Quantity]], prices: Dict[str, Money]
    ) -> PortfolioAllocation:
        """Calculate allocation by stock grades."""
        if not portfolio:
            return PortfolioAllocation({}, Money.zero(self.config.default_currency))

        total_value = self.calculate_total_value(portfolio, prices)
        grade_values: Dict[str, Decimal] = {}

        for stock, quantity in portfolio:
            grade = stock.grade.value if stock.grade else "Ungraded"
            symbol_str = str(stock.symbol)
            current_price = prices[symbol_str]
            position_value = self.calculate_position_value(
                stock, quantity, current_price
            )

            if grade not in grade_values:
                grade_values[grade] = Decimal("0")
            grade_values[grade] += position_value.amount

        # Convert to percentages
        grade_percentages = {}
        for grade, value in grade_values.items():
            percentage = (
                (value / total_value.amount) * Decimal("100")
                if total_value.amount > 0
                else Decimal("0")
            )
            grade_percentages[grade] = percentage

        return PortfolioAllocation(grade_percentages, total_value)

    def calculate_diversity_score(
        self, portfolio: List[Tuple[StockEntity, Quantity]], prices: Dict[str, Money]
    ) -> Decimal:
        """Calculate how well diversified the portfolio is (0-1 scale)."""
        if len(portfolio) < 2:
            return Decimal("0")

        position_allocations = self.calculate_position_allocations(portfolio, prices)

        # Calculate Herfindahl-Hirschman Index (HHI) for concentration
        hhi = sum(
            (allocation.percentage / Decimal("100")) ** 2
            for allocation in position_allocations
        )

        # Convert HHI to diversity score (lower HHI = higher diversity)
        # Perfect diversification (equal weights) would have HHI = 1/n
        n = len(portfolio)
        min_hhi = Decimal("1") / Decimal(str(n))  # Perfect equal weighting
        max_hhi = Decimal("1")  # All money in one stock

        # Normalize to 0-1 scale where 1 = perfectly diversified
        if max_hhi == min_hhi:
            return Decimal("1")

        diversity_score = (max_hhi - hhi) / (max_hhi - min_hhi)
        return max(Decimal("0"), min(Decimal("1"), diversity_score))

    def calculate_weighted_average_grade(
        self, portfolio: List[Tuple[StockEntity, Quantity]], prices: Dict[str, Money]
    ) -> str:
        """Calculate portfolio's weighted average grade."""
        if not portfolio:
            return "N/A"

        # Grade to numeric mapping
        grade_values = {"A": 4.0, "B": 3.0, "C": 2.0}

        total_value = self.calculate_total_value(portfolio, prices)
        if total_value.amount == 0:
            return "N/A"

        weighted_sum = Decimal("0")
        total_weight = Decimal("0")

        for stock, quantity in portfolio:
            if stock.grade and stock.grade.value in grade_values:
                symbol_str = str(stock.symbol)
                current_price = prices[symbol_str]
                position_value = self.calculate_position_value(
                    stock, quantity, current_price
                )
                weight = position_value.amount / total_value.amount
                weighted_sum += Decimal(str(grade_values[stock.grade.value])) * weight
                total_weight += weight

        if total_weight == 0:
            return "N/A"

        avg_numeric = weighted_sum / total_weight

        # Convert back to letter grade
        if avg_numeric >= 3.5:
            return "A"
        if avg_numeric >= 2.5:
            return "B"
        return "C"

    def generate_portfolio_summary(
        self, portfolio: List[Tuple[StockEntity, Quantity]], prices: Dict[str, Money]
    ) -> PortfolioSummary:
        """Generate comprehensive portfolio summary."""
        if not portfolio:
            return PortfolioSummary(
                total_value=Money.zero(self.config.default_currency),
                position_count=0,
                top_holding=None,
                industry_breakdown={},
                grade_breakdown={},
                risk_level="N/A",
                diversification_grade="N/A",
            )

        total_value = self.calculate_total_value(portfolio, prices)
        position_allocations = self.calculate_position_allocations(portfolio, prices)
        industry_allocation = self.calculate_industry_allocations(portfolio, prices)
        grade_allocation = self.calculate_grade_allocations(portfolio, prices)
        diversity_score = self.calculate_diversity_score(portfolio, prices)

        # Find top holding
        top_holding = (
            max(position_allocations, key=lambda x: x.percentage)
            if position_allocations
            else None
        )

        # Determine diversification grade
        if diversity_score >= Decimal("0.8"):
            diversification_grade = "A"
        elif diversity_score >= Decimal("0.6"):
            diversification_grade = "B"
        elif diversity_score >= Decimal("0.4"):
            diversification_grade = "C"
        else:
            diversification_grade = "D"

        # Simple risk level assessment
        high_risk_percentage = grade_allocation.get_allocation_percentage("C")
        if high_risk_percentage >= Decimal("50"):
            risk_level = "High"
        elif high_risk_percentage >= Decimal("25"):
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return PortfolioSummary(
            total_value=total_value,
            position_count=len(portfolio),
            top_holding=top_holding,
            industry_breakdown=industry_allocation.allocations,
            grade_breakdown=grade_allocation.allocations,
            risk_level=risk_level,
            diversification_grade=diversification_grade,
        )
