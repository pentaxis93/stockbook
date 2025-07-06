"""Stock-related domain events.

Events that represent significant occurrences in the stock subdomain.
"""

from datetime import datetime

from src.domain.events.base import DomainEvent
from src.domain.value_objects.stock_symbol import StockSymbol


class StockAddedEvent(DomainEvent):
    """Event raised when a new stock is added to the system.

    This event can be used by other parts of the system to react to
    new stocks being available for trading.
    """

    def __init__(
        self,
        stock_symbol: StockSymbol,
        stock_name: str,
        stock_id: int,
        occurred_at: datetime | None = None,
    ):
        """Initialize StockAddedEvent.

        Args:
            stock_symbol: Symbol of the added stock
            stock_name: Name of the company
            stock_id: Database ID of the stock
            occurred_at: When the event occurred

        Raises:
            ValueError: If validation fails
        """
        super().__init__(occurred_at)

        # Validate inputs
        if not stock_name or not stock_name.strip():
            raise ValueError("Stock name cannot be empty")

        if stock_id <= 0:
            raise ValueError("Stock ID must be positive")

        self._stock_symbol = stock_symbol
        self._stock_name = stock_name.strip()
        self._stock_id = stock_id

    @property
    def stock_symbol(self) -> StockSymbol:
        """Get the stock symbol."""
        return self._stock_symbol

    @property
    def stock_name(self) -> str:
        """Get the stock name."""
        return self._stock_name

    @property
    def stock_id(self) -> int:
        """Get the stock ID."""
        return self._stock_id

    def __str__(self) -> str:
        """String representation for display."""
        return f"StockAddedEvent(symbol={self.stock_symbol}, name={self.stock_name!r})"

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"StockAddedEvent(stock_symbol={self.stock_symbol!r}, "
            f"stock_name={self.stock_name!r}, stock_id={self.stock_id}, "
            f"occurred_at={self.occurred_at.isoformat()})"
        )
