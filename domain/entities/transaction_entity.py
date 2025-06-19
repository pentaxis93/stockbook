"""
Transaction aggregate root entity.

Rich domain entity implementing clean architecture with value objects.
Follows Domain-Driven Design principles with business logic encapsulation.
"""

from datetime import date
from typing import Optional

from domain.value_objects import Notes, TransactionType
from shared_kernel.value_objects import Money, Quantity


class TransactionEntity:
    """
    Transaction aggregate root representing a stock trade.

    Rich domain entity with value objects and business logic.
    Follows clean architecture and Domain-Driven Design principles.
    """

    def __init__(
        self,
        portfolio_id: int,
        stock_id: int,
        transaction_type: TransactionType,
        quantity: Quantity,
        price: Money,
        transaction_date: date,
        notes: Optional[Notes] = None,
        transaction_id: Optional[int] = None,
    ):
        """Initialize transaction with required value objects and validation."""
        # Validate primitive IDs
        if not isinstance(portfolio_id, int) or portfolio_id <= 0:
            raise ValueError("Portfolio ID must be positive")
        if not isinstance(stock_id, int) or stock_id <= 0:
            raise ValueError("Stock ID must be positive")

        # Store validated attributes
        self._id = transaction_id
        self._portfolio_id = portfolio_id
        self._stock_id = stock_id
        self._transaction_type = transaction_type
        self._quantity = quantity
        self._price = price
        self._transaction_date = transaction_date
        self._notes = notes or Notes("")

    # Identity
    @property
    def id(self) -> Optional[int]:
        """Get transaction ID."""
        return self._id

    # Core attributes
    @property
    def portfolio_id(self) -> int:
        """Get portfolio ID."""
        return self._portfolio_id

    @property
    def stock_id(self) -> int:
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

    def set_id(self, transaction_id: int) -> None:
        """Set transaction ID (for persistence layer)."""
        if not isinstance(transaction_id, int) or transaction_id <= 0:
            raise ValueError("ID must be a positive integer")
        if self._id is not None:
            raise ValueError("ID is already set and cannot be changed")
        self._id = transaction_id

    # Equality and representation
    def __eq__(self, other) -> bool:
        """Check equality based on business identity."""
        if not isinstance(other, TransactionEntity):
            return False
        return (
            self._portfolio_id == other._portfolio_id
            and self._stock_id == other._stock_id
            and self._transaction_type == other._transaction_type
            and self._quantity == other._quantity
            and self._price == other._price
            and self._transaction_date == other._transaction_date
        )

    def __hash__(self) -> int:
        """Hash for use in collections."""
        return hash(
            (
                self._portfolio_id,
                self._stock_id,
                self._transaction_type,
                self._quantity,
                self._price,
                self._transaction_date,
            )
        )

    def __str__(self) -> str:
        """String representation."""
        return f"{self._transaction_type} {self._quantity.value} @ {self._price} on {self._transaction_date}"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"TransactionEntity(portfolio_id={self._portfolio_id}, stock_id={self._stock_id}, type='{self._transaction_type.value}', quantity={self._quantity.value}, price={self._price})"
