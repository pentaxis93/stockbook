"""Transaction aggregate root entity.

Rich domain entity implementing clean architecture with value objects.
Follows Domain-Driven Design principles with business logic encapsulation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from src.domain.entities.entity import Entity
from src.domain.value_objects import Money, Notes, Quantity, TransactionType


if TYPE_CHECKING:
    from datetime import date


class Transaction(Entity):
    """Transaction aggregate root representing a stock trade.

    Rich domain entity with value objects and business logic.
    Follows clean architecture and Domain-Driven Design principles.
    """

    class Builder:
        """Builder for Transaction to manage multiple parameters elegantly."""

        def __init__(self) -> None:
            """Initialize builder with default values."""
            self.portfolio_id: str | None = None
            self.stock_id: str | None = None
            self.transaction_type: TransactionType | None = None
            self.quantity: Quantity | None = None
            self.price: Money | None = None
            self.transaction_date: date | None = None
            self.notes: Notes | None = None
            self.entity_id: str | None = None

        def with_portfolio_id(self, portfolio_id: str) -> Self:
            """Set the portfolio ID."""
            self.portfolio_id = portfolio_id
            return self

        def with_stock_id(self, stock_id: str) -> Self:
            """Set the stock ID."""
            self.stock_id = stock_id
            return self

        def with_transaction_type(self, transaction_type: TransactionType) -> Self:
            """Set the transaction type."""
            self.transaction_type = transaction_type
            return self

        def with_quantity(self, quantity: Quantity) -> Self:
            """Set the quantity."""
            self.quantity = quantity
            return self

        def with_price(self, price: Money) -> Self:
            """Set the price."""
            self.price = price
            return self

        def with_transaction_date(self, transaction_date: date) -> Self:
            """Set the transaction date."""
            self.transaction_date = transaction_date
            return self

        def with_notes(self, notes: Notes | None) -> Self:
            """Set the notes."""
            self.notes = notes
            return self

        def with_id(self, entity_id: str | None) -> Self:
            """Set the entity ID."""
            self.entity_id = entity_id
            return self

        def build(self) -> Transaction:
            """Build and return the Transaction instance."""
            return Transaction(_builder_instance=self)

    def __init__(self, *, _builder_instance: Transaction.Builder | None = None):
        """Initialize transaction through builder pattern."""
        if _builder_instance is None:
            raise ValueError("Transaction must be created through Builder")

        # Extract values from builder
        portfolio_id = _builder_instance.portfolio_id
        stock_id = _builder_instance.stock_id
        transaction_type = _builder_instance.transaction_type
        quantity = _builder_instance.quantity
        price = _builder_instance.price
        transaction_date = _builder_instance.transaction_date
        notes = _builder_instance.notes
        entity_id = _builder_instance.entity_id

        # Validate required fields
        if portfolio_id is None:
            raise ValueError("Portfolio ID is required")
        if stock_id is None:
            raise ValueError("Stock ID is required")
        if transaction_type is None:
            raise ValueError("Transaction type is required")
        if quantity is None:
            raise ValueError("Quantity is required")
        if price is None:
            raise ValueError("Price is required")
        if transaction_date is None:
            raise ValueError("Transaction date is required")

        # Validate foreign key IDs are not empty
        if not portfolio_id:
            raise ValueError("Portfolio ID must be a non-empty string")
        if not stock_id:
            raise ValueError("Stock ID must be a non-empty string")

        # Store validated attributes
        super().__init__(id=entity_id)
        self._portfolio_id = portfolio_id
        self._stock_id = stock_id
        self._transaction_type = transaction_type
        self._quantity = quantity
        self._price = price
        self._transaction_date = transaction_date
        self._notes = notes or Notes("")

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
    def transaction_type(self) -> TransactionType:
        """Get transaction type."""
        return self._transaction_type

    @property
    def quantity(self) -> Quantity:
        """Get quantity."""
        return self._quantity

    @property
    def price(self) -> Money:
        """Get price."""
        return self._price

    @property
    def transaction_date(self) -> date:
        """Get transaction date."""
        return self._transaction_date

    @property
    def notes(self) -> Notes:
        """Get notes."""
        return self._notes

    # Business methods
    def calculate_total_value(self) -> Money:
        """Calculate total transaction value (quantity * price)."""
        return self._price * self._quantity.value

    def is_buy(self) -> bool:
        """Check if this is a buy transaction."""
        return self._transaction_type.is_buy()

    def is_sell(self) -> bool:
        """Check if this is a sell transaction."""
        return self._transaction_type.is_sell()

    def has_notes(self) -> bool:
        """Check if transaction has notes."""
        return self._notes.has_content()

    # Representation

    def __str__(self) -> str:
        """String representation."""
        return (
            f"{self._transaction_type} {self._quantity.value} @ {self._price} "
            f"on {self._transaction_date}"
        )

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"Transaction(portfolio_id={self._portfolio_id}, "
            f"stock_id={self._stock_id}, type={self._transaction_type.value!r}, "
            f"quantity={self._quantity.value}, price={self._price})"
        )
