"""Position domain entity for stock holdings in portfolios."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from .entity import Entity

if TYPE_CHECKING:
    from decimal import Decimal
    from typing import Self

    from src.domain.value_objects.money import Money
    from src.domain.value_objects.quantity import Quantity

UTC = ZoneInfo("UTC")


class Position(Entity):
    """Position aggregate root representing stock holdings in a portfolio.

    Rich domain entity with value objects and business logic.
    Follows clean architecture and Domain-Driven Design principles.
    """

    class Builder:
        """Builder for Position to manage multiple parameters elegantly."""

        def __init__(self) -> None:
            """Initialize builder with default values."""
            self.portfolio_id: str | None = None
            self.stock_id: str | None = None
            self.quantity: Quantity | None = None
            self.average_cost: Money | None = None
            self.last_transaction_date: datetime | None = None
            self.entity_id: str | None = None

        def with_portfolio_id(self, portfolio_id: str) -> Self:
            """Set the portfolio ID."""
            self.portfolio_id = portfolio_id
            return self

        def with_stock_id(self, stock_id: str) -> Self:
            """Set the stock ID."""
            self.stock_id = stock_id
            return self

        def with_quantity(self, quantity: Quantity) -> Self:
            """Set the quantity."""
            self.quantity = quantity
            return self

        def with_average_cost(self, average_cost: Money) -> Self:
            """Set the average cost."""
            self.average_cost = average_cost
            return self

        def with_last_transaction_date(
            self,
            last_transaction_date: datetime | None,
        ) -> Self:
            """Set the last transaction date."""
            self.last_transaction_date = last_transaction_date
            return self

        def with_id(self, entity_id: str | None) -> Self:
            """Set the entity ID."""
            self.entity_id = entity_id
            return self

        def build(self) -> Position:
            """Build and return the Position instance."""
            return Position(_builder_instance=self)

    def __init__(self, *, _builder_instance: Position.Builder | None = None) -> None:
        """Initialize position through builder pattern."""
        if _builder_instance is None:
            msg = "Position must be created through Builder"
            raise ValueError(msg)

        # Extract values from builder
        portfolio_id = _builder_instance.portfolio_id
        stock_id = _builder_instance.stock_id
        quantity = _builder_instance.quantity
        average_cost = _builder_instance.average_cost
        last_transaction_date = _builder_instance.last_transaction_date
        entity_id = _builder_instance.entity_id

        # Validate required fields
        if portfolio_id is None:
            msg = "Portfolio ID is required"
            raise ValueError(msg)
        if stock_id is None:
            msg = "Stock ID is required"
            raise ValueError(msg)
        if quantity is None:
            msg = "Quantity is required"
            raise ValueError(msg)
        if average_cost is None:
            msg = "Average cost is required"
            raise ValueError(msg)

        # Validate foreign key IDs are not empty
        if not portfolio_id:
            msg = "Portfolio ID must be a non-empty string"
            raise ValueError(msg)
        if not stock_id:
            msg = "Stock ID must be a non-empty string"
            raise ValueError(msg)

        # Store validated attributes
        super().__init__(id=entity_id)
        self._portfolio_id = portfolio_id
        self._stock_id = stock_id
        self._quantity = quantity
        self._average_cost = average_cost
        self._last_transaction_date = last_transaction_date

    # Core attributes
    @property
    def portfolio_id(self) -> str:
        """Get portfolio ID."""
        return self._portfolio_id

    @property
    def stock_id(self) -> str:
        """Get stock ID."""
        return self._stock_id

    @property
    def quantity(self) -> Quantity:
        """Get quantity."""
        return self._quantity

    @property
    def average_cost(self) -> Money:
        """Get average cost."""
        return self._average_cost

    @property
    def last_transaction_date(self) -> datetime | None:
        """Get last transaction date."""
        return self._last_transaction_date

    # Business methods
    def calculate_total_cost(self) -> Money:
        """Calculate total cost of position (quantity * average_cost)."""
        return self._average_cost * self._quantity.value

    def calculate_current_value(self, current_price: Money) -> Money:
        """Calculate current value of position (quantity * current_price)."""
        return current_price * self._quantity.value

    def calculate_gain_loss(self, current_price: Money) -> Money:
        """Calculate gain/loss of position (current_value - total_cost)."""
        current_value = self.calculate_current_value(current_price)
        total_cost = self.calculate_total_cost()
        return current_value - total_cost

    def calculate_gain_loss_percentage(self, current_price: Money) -> Decimal:
        """Calculate gain/loss percentage of position."""
        total_cost = self.calculate_total_cost()
        if total_cost.amount == 0:
            msg = "Cannot calculate percentage with zero cost"
            raise ZeroDivisionError(msg)

        gain_loss = self.calculate_gain_loss(current_price)
        return (gain_loss.amount / total_cost.amount) * 100

    def is_profitable(self, current_price: Money) -> bool:
        """Check if position is profitable at current price."""
        return self.calculate_current_value(current_price) > self.calculate_total_cost()

    def add_shares(self, quantity: Quantity, price: Money) -> None:
        """Add shares to position and update average cost using weighted average."""
        if quantity.value == 0:
            return  # No change needed

        # Calculate weighted average cost
        current_total_cost = self.calculate_total_cost()
        new_shares_cost = price * quantity.value
        new_total_cost = current_total_cost + new_shares_cost
        new_total_quantity = self._quantity + quantity

        # Update position
        self._quantity = new_total_quantity
        self._average_cost = new_total_cost / new_total_quantity.value
        self._last_transaction_date = datetime.now(UTC)

    def remove_shares(self, quantity: Quantity) -> None:
        """Remove shares from position while preserving average cost."""
        if quantity.value == 0:
            return  # No change needed

        if quantity > self._quantity:
            msg = "Cannot remove more shares than currently held"
            raise ValueError(msg)

        # Update quantity (preserve average cost)
        self._quantity = self._quantity - quantity
        self._last_transaction_date = datetime.now(UTC)

    # Representation
    def __str__(self) -> str:
        """String representation."""
        return f"{self._quantity.value} shares @ {self._average_cost} avg cost"

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"Position(portfolio_id={self._portfolio_id}, "
            f"stock_id={self._stock_id}, "
            f"quantity={self._quantity.value}, average_cost={self._average_cost})"
        )
