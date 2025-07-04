"""
Transaction aggregate root entity.

Rich domain entity implementing clean architecture with value objects.
Follows Domain-Driven Design principles with business logic encapsulation.
"""

from datetime import date
from typing import Optional

from src.domain.entities.entity import Entity
from src.domain.value_objects import Money, Notes, Quantity, TransactionType


class Transaction(Entity):
    """
    Transaction aggregate root representing a stock trade.

    Rich domain entity with value objects and business logic.
    Follows clean architecture and Domain-Driven Design principles.
    """

    def __init__(  # pylint: disable=too-many-arguments
        # Rationale: Transaction is a core domain entity that requires all these attributes
        # to properly represent a stock trade. Each parameter is essential and represents
        # a distinct aspect of the transaction. Using a parameter object would obscure
        # the clear intent and reduce readability without meaningful benefit.
        self,
        portfolio_id: str,
        stock_id: str,
        transaction_type: TransactionType,
        quantity: Quantity,
        price: Money,
        transaction_date: date,
        *,
        notes: Optional[Notes] = None,
        id: Optional[str] = None,
    ):
        """Initialize transaction with required value objects and validation."""
        # Validate foreign key IDs are not empty
        if not portfolio_id:
            raise ValueError("Portfolio ID must be a non-empty string")
        if not stock_id:
            raise ValueError("Stock ID must be a non-empty string")

        # Store validated attributes
        super().__init__(id=id)
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
        return f"{self._transaction_type} {self._quantity.value} @ {self._price} on {self._transaction_date}"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Transaction(portfolio_id={self._portfolio_id}, stock_id={self._stock_id}, type={self._transaction_type.value!r}, quantity={self._quantity.value}, price={self._price})"
