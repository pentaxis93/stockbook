"""
Portfolio calculation service.

Provides business logic for portfolio-level calculations that operate
across multiple stocks and provide aggregated insights.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from src.domain.entities.stock_entity import StockEntity
from src.domain.value_objects import Money, Quantity

from .exceptions import CalculationError
from .value_objects import (
    PortfolioAllocation,
    PositionAllocation,
)


@dataclass(frozen=True)
class PortfolioCalculationConfig:
    """Configuration for portfolio calculation rules."""

    concentration_threshold: Decimal = field(
        default_factory=lambda: Decimal("0.15")
    )  # 15% max per position
    minimum_diversification_score: Decimal = field(
        default_factory=lambda: Decimal("0.6")
    )
    default_currency: str = "USD"


class PortfolioCalculationService:
    """
    Service for portfolio-level calculations and analysis.

    Handles calculations that operate across multiple stocks and provide
    aggregated portfolio insights and metrics.
    """

    def __init__(self, config: Optional[PortfolioCalculationConfig] = None):
        """Initialize portfolio calculation service with optional configuration.

        Args:
            config: Configuration settings for portfolio calculations, uses defaults if None
        """
        self.config = config or PortfolioCalculationConfig()

    def calculate_total_value(
        self, portfolio: List[Tuple[StockEntity, Quantity]], prices: Dict[str, Money]
    ) -> Money:
        """Calculate total portfolio market value."""
        if not portfolio:
            return Money.zero()

        total_amount = Decimal("0")

        for stock, quantity in portfolio:
            symbol_str = str(stock.symbol)
            if symbol_str not in prices:
                raise CalculationError(
                    f"Stock {stock.symbol} missing current price",
                    operation="total_value",
                )

            current_price = prices[symbol_str]
            position_value = current_price.amount * Decimal(str(quantity.value))
            total_amount += position_value

        return Money(total_amount)

    def calculate_position_value(
        self, _stock: StockEntity, quantity: Quantity, current_price: Money
    ) -> Money:
        """Calculate individual position value."""
        return Money(current_price.amount * Decimal(str(quantity.value)))

    def calculate_position_allocations(
        self, portfolio: List[Tuple[StockEntity, Quantity]], prices: Dict[str, Money]
    ) -> List[PositionAllocation]:
        """Calculate allocation percentage for each position."""
        if not portfolio:
            return []

        total_value = self.calculate_total_value(portfolio, prices)
        if total_value.amount == 0:
            return []

        allocations: List[PositionAllocation] = []
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
            return PortfolioAllocation({}, Money.zero())

        total_value = self.calculate_total_value(portfolio, prices)
        industry_values = self._calculate_industry_values(portfolio, prices)
        industry_percentages = self._convert_to_percentages(
            industry_values, total_value
        )

        return PortfolioAllocation(industry_percentages, total_value)

    def _calculate_industry_values(
        self, portfolio: List[Tuple[StockEntity, Quantity]], prices: Dict[str, Money]
    ) -> Dict[str, Decimal]:
        """Calculate total values by industry."""
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

        return industry_values

    def _convert_to_percentages(
        self, industry_values: Dict[str, Decimal], total_value: Money
    ) -> Dict[str, Decimal]:
        """Convert industry values to percentages."""
        industry_percentages: Dict[str, Decimal] = {}
        for industry, value in industry_values.items():
            percentage = (
                (value / total_value.amount) * Decimal("100")
                if total_value.amount > 0
                else Decimal("0")
            )
            industry_percentages[industry] = percentage

        return industry_percentages
