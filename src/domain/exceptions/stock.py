"""Stock-specific domain exceptions."""

from typing import Any

from .base import AlreadyExistsError, BusinessRuleViolationError, NotFoundError


class StockNotFoundError(NotFoundError):
    """Exception raised when a stock is not found."""

    def __init__(self, identifier: Any) -> None:
        """Initialize StockNotFoundError.

        Args:
            identifier: The stock ID or symbol that was not found
        """
        super().__init__(entity_type="Stock", identifier=identifier)


class StockAlreadyExistsError(AlreadyExistsError):
    """Exception raised when a stock already exists."""

    def __init__(self, symbol: str) -> None:
        """Initialize StockAlreadyExistsError.

        Args:
            symbol: The stock symbol that already exists
        """
        self.symbol = symbol
        super().__init__(entity_type="Stock", identifier=symbol)


class InvalidStockSymbolError(BusinessRuleViolationError):
    """Exception raised when a stock symbol is invalid."""

    def __init__(self, symbol: str, reason: str | None = None) -> None:
        """Initialize InvalidStockSymbolError.

        Args:
            symbol: The invalid stock symbol
            reason: Optional reason for why the symbol is invalid
        """
        self.symbol = symbol
        context = {
            "symbol": symbol,
            "reason": reason or self._default_reason(symbol),
        }
        super().__init__(rule="valid_stock_symbol", context=context)

    def _default_reason(self, symbol: str) -> str:
        """Provide default reason based on symbol."""
        if not symbol:
            return "Symbol cannot be empty"
        return "Invalid stock symbol format"


class InvalidStockGradeError(BusinessRuleViolationError):
    """Exception raised when a stock grade is invalid."""

    def __init__(
        self,
        grade: str | None,
        valid_grades: list[str] | None = None,
    ) -> None:
        """Initialize InvalidStockGradeError.

        Args:
            grade: The invalid stock grade
            valid_grades: Optional list of valid grades (defaults to standard grades)
        """
        self.grade = grade
        context = {
            "grade": grade,
            "valid_grades": valid_grades or ["A", "B", "C", "D", "F"],
        }
        super().__init__(rule="valid_stock_grade", context=context)
