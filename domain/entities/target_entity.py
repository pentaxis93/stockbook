"""
Target aggregate root entity.

Placeholder implementation for target domain entity to replace
legacy Pydantic model dependency in repository interfaces.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from shared_kernel.value_objects import Money


@dataclass
class TargetEntity:
    """
    Target aggregate root representing investment price targets.

    TODO: Implement full domain entity with business logic, validation,
    and rich behavior. This is currently a placeholder to remove
    legacy model dependencies from repository interfaces.
    """

    # Identity
    id: Optional[int] = None

    # Core attributes
    portfolio_id: int = 0
    stock_id: int = 0
    pivot_price: Optional[Money] = None  # Target price for entry/exit
    failure_price: Optional[Money] = None  # Stop-loss price
    status: str = "active"  # 'active', 'hit', 'failed', 'cancelled'
    created_date: Optional[date] = None
    notes: Optional[str] = None

    def __post_init__(self):
        """Validate target data after initialization."""
        if self.status not in ["active", "hit", "failed", "cancelled"]:
            raise ValueError("Invalid target status")

        if self.portfolio_id <= 0:
            raise ValueError("Portfolio ID must be positive")

        if self.stock_id <= 0:
            raise ValueError("Stock ID must be positive")

        if self.pivot_price is None:
            raise ValueError("Pivot price cannot be None")

        if self.failure_price is None:
            raise ValueError("Failure price cannot be None")

    def __str__(self) -> str:
        """String representation."""
        return f"Target(pivot: {self.pivot_price}, failure: {self.failure_price}, status={self.status})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"TargetEntity(id={self.id}, pivot={self.pivot_price}, status='{self.status}')"
