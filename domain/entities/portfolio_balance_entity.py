"""
Portfolio Balance entity.

Placeholder implementation for portfolio balance domain entity to replace
legacy Pydantic model dependency in repository interfaces.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from shared_kernel.value_objects import Money


@dataclass
class PortfolioBalanceEntity:
    """
    Portfolio Balance entity representing portfolio value at a specific date.

    TODO: Implement full domain entity with business logic, validation,
    and rich behavior. This is currently a placeholder to remove
    legacy model dependencies from repository interfaces.
    """

    # Identity
    id: Optional[int] = None

    # Core attributes
    portfolio_id: int = 0
    balance_date: Optional[date] = None
    withdrawals: Optional[Money] = None
    deposits: Optional[Money] = None
    final_balance: Optional[Money] = None
    index_change: Optional[float] = None  # Percentage change

    def __post_init__(self):
        """Validate balance data after initialization."""
        if self.portfolio_id <= 0:
            raise ValueError("Portfolio ID must be positive")

        if self.balance_date is None:
            raise ValueError("Balance date cannot be None")

        if self.final_balance is None:
            raise ValueError("Final balance cannot be None")

    def __str__(self) -> str:
        """String representation."""
        return f"Balance({self.balance_date}: {self.final_balance})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"PortfolioBalanceEntity(id={self.id}, portfolio_id={self.portfolio_id}, date={self.balance_date})"
