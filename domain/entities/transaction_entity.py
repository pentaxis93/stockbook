"""
Transaction aggregate root entity.

Placeholder implementation for transaction domain entity to replace
legacy Pydantic model dependency in repository interfaces.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from shared_kernel.value_objects import Money, Quantity


@dataclass
class TransactionEntity:
    """
    Transaction aggregate root representing a stock trade.

    TODO: Implement full domain entity with business logic, validation,
    and rich behavior. This is currently a placeholder to remove
    legacy model dependencies from repository interfaces.
    """

    # Identity
    id: Optional[int] = None

    # Core attributes
    portfolio_id: int = 0
    stock_id: int = 0
    transaction_type: str = ""  # 'buy' or 'sell'
    quantity: Optional[Quantity] = None
    price: Optional[Money] = None
    transaction_date: Optional[date] = None
    notes: Optional[str] = None

    def __post_init__(self):
        """Validate transaction data after initialization."""
        if not self.transaction_type:
            raise ValueError("Transaction type cannot be empty")

        if self.transaction_type not in ["buy", "sell"]:
            raise ValueError("Transaction type must be 'buy' or 'sell'")

        if self.portfolio_id <= 0:
            raise ValueError("Portfolio ID must be positive")

        if self.stock_id <= 0:
            raise ValueError("Stock ID must be positive")

    def __str__(self) -> str:
        """String representation."""
        return f"Transaction({self.transaction_type} {self.quantity} @ {self.price})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"TransactionEntity(id={self.id}, type='{self.transaction_type}', portfolio_id={self.portfolio_id})"
