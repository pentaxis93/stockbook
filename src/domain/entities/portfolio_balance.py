"""Portfolio Balance entity.

Rich domain entity implementing clean architecture with value objects.
Follows Domain-Driven Design principles with business logic encapsulation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from src.domain.entities.entity import Entity
from src.domain.value_objects import IndexChange, Money

if TYPE_CHECKING:
    from datetime import date


class PortfolioBalance(Entity):
    """Portfolio Balance entity representing portfolio value at a specific date.

    Rich domain entity with value objects and business logic.
    Follows clean architecture and Domain-Driven Design principles.
    """

    class Builder:
        """Builder for PortfolioBalance to manage multiple parameters elegantly."""

        def __init__(self) -> None:
            """Initialize builder with default values."""
            self.portfolio_id: str | None = None
            self.balance_date: date | None = None
            self.final_balance: Money | None = None
            self.withdrawals: Money | None = None
            self.deposits: Money | None = None
            self.index_change: IndexChange | None = None
            self.entity_id: str | None = None

        def with_portfolio_id(self, portfolio_id: str) -> Self:
            """Set the portfolio ID."""
            self.portfolio_id = portfolio_id
            return self

        def with_balance_date(self, balance_date: date) -> Self:
            """Set the balance date."""
            self.balance_date = balance_date
            return self

        def with_final_balance(self, final_balance: Money) -> Self:
            """Set the final balance."""
            self.final_balance = final_balance
            return self

        def with_withdrawals(self, withdrawals: Money | None) -> Self:
            """Set the withdrawals."""
            self.withdrawals = withdrawals
            return self

        def with_deposits(self, deposits: Money | None) -> Self:
            """Set the deposits."""
            self.deposits = deposits
            return self

        def with_index_change(self, index_change: IndexChange | None) -> Self:
            """Set the index change."""
            self.index_change = index_change
            return self

        def with_id(self, entity_id: str | None) -> Self:
            """Set the entity ID."""
            self.entity_id = entity_id
            return self

        def build(self) -> PortfolioBalance:
            """Build and return the PortfolioBalance instance."""
            return PortfolioBalance(_builder_instance=self)

    def __init__(
        self, *, _builder_instance: PortfolioBalance.Builder | None = None
    ) -> None:
        """Initialize portfolio balance through builder pattern."""
        if _builder_instance is None:
            raise ValueError("PortfolioBalance must be created through Builder")

        # Extract values from builder
        portfolio_id = _builder_instance.portfolio_id
        balance_date = _builder_instance.balance_date
        final_balance = _builder_instance.final_balance
        withdrawals = _builder_instance.withdrawals
        deposits = _builder_instance.deposits
        index_change = _builder_instance.index_change
        entity_id = _builder_instance.entity_id

        # Validate required fields
        if portfolio_id is None:
            raise ValueError("Portfolio ID is required")
        if balance_date is None:
            raise ValueError("Balance date is required")
        if final_balance is None:
            raise ValueError("Final balance is required")

        # Validate foreign key ID is not empty
        if not portfolio_id:
            raise ValueError("Portfolio ID must be a non-empty string")

        # Initialize parent
        super().__init__(id=entity_id)

        # Store validated attributes
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
    def index_change(self) -> IndexChange | None:
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

    def update_index_change(self, index_change: IndexChange | float | None) -> None:
        """Update index change."""
        if index_change is None:
            self._index_change = None
        elif isinstance(index_change, int | float):
            self._index_change = IndexChange(index_change)
        else:
            self._index_change = index_change

    # Representation

    def __str__(self) -> str:
        """String representation."""
        return f"Balance({self._balance_date}: {self._final_balance})"

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"PortfolioBalance(portfolio_id={self._portfolio_id}, "
            f"date={self._balance_date})"
        )
