"""
Portfolio Balance entity.

Rich domain entity implementing clean architecture with value objects.
Follows Domain-Driven Design principles with business logic encapsulation.
"""

from datetime import date
from typing import Optional, Union

from src.domain.entities.base import BaseEntity
from src.domain.value_objects import IndexChange, Money


class PortfolioBalanceEntity(BaseEntity):
    """
    Portfolio Balance entity representing portfolio value at a specific date.

    Rich domain entity with value objects and business logic.
    Follows clean architecture and Domain-Driven Design principles.
    """

    def __init__(
        self,
        portfolio_id: str,
        balance_date: date,
        final_balance: Money,
        withdrawals: Optional[Money] = None,
        deposits: Optional[Money] = None,
        index_change: Optional[IndexChange] = None,
        entity_id: Optional[str] = None,
    ):
        """Initialize portfolio balance with required value objects and validation."""
        # Validate foreign key ID is not empty
        if not portfolio_id or not isinstance(portfolio_id, str):
            raise ValueError("Portfolio ID must be a non-empty string")

        # Store validated attributes
        super().__init__(entity_id=entity_id)
        self._portfolio_id = portfolio_id
        self._balance_date = balance_date
        self._final_balance = final_balance
        self._withdrawals = withdrawals or Money.zero()
        self._deposits = deposits or Money.zero()
        self._index_change = index_change

    @property
    def portfolio_id(self) -> str:
        """Get portfolio ID."""
        return self._portfolio_id

    # Core attributes
    @property
    def balance_date(self) -> date:
        """Get balance date."""
        return self._balance_date

    @property
    def final_balance(self) -> Money:
        """Get final balance."""
        return self._final_balance

    @property
    def withdrawals(self) -> Money:
        """Get withdrawals."""
        return self._withdrawals

    @property
    def deposits(self) -> Money:
        """Get deposits."""
        return self._deposits

    @property
    def index_change(self) -> Optional[IndexChange]:
        """Get index change."""
        return self._index_change

    # Business methods
    def calculate_net_flow(self) -> Money:
        """Calculate net cash flow (deposits - withdrawals)."""
        return self._deposits - self._withdrawals

    def has_positive_change(self) -> bool:
        """Check if portfolio has positive index change."""
        return self._index_change is not None and self._index_change.is_positive()

    def has_negative_change(self) -> bool:
        """Check if portfolio has negative index change."""
        return self._index_change is not None and self._index_change.is_negative()

    def had_deposits(self) -> bool:
        """Check if portfolio had deposits."""
        return not self._deposits.is_zero()

    def had_withdrawals(self) -> bool:
        """Check if portfolio had withdrawals."""
        return not self._withdrawals.is_zero()

    def update_index_change(
        self, index_change: Union[IndexChange, float, None]
    ) -> None:
        """Update index change."""
        if index_change is None:
            self._index_change = None
        elif isinstance(index_change, (int, float)):
            self._index_change = IndexChange(index_change)
        else:
            self._index_change = index_change

    # Equality and representation
    def __eq__(self, other) -> bool:
        """Check equality based on business identity (portfolio_id, balance_date)."""
        if not isinstance(other, PortfolioBalanceEntity):
            return False
        return (
            self._portfolio_id == other._portfolio_id
            and self._balance_date == other._balance_date
        )

    def __hash__(self) -> int:
        """Hash for use in collections based on business identity."""
        return hash((self._portfolio_id, self._balance_date))

    def __str__(self) -> str:
        """String representation."""
        return f"Balance({self._balance_date}: {self._final_balance})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"PortfolioBalanceEntity(portfolio_id={self._portfolio_id}, date={self._balance_date})"
