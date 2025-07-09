"""Stock-specific domain exceptions.

This module defines exceptions specific to stock-related operations.
These exceptions provide clear, domain-specific error messages for
stock validation and business rule violations.

Usage Examples:
    >>> # Stock not found
    >>> raise StockNotFoundError("AAPL")
    StockNotFoundError: Stock with identifier 'AAPL' not found

    >>> # Stock already exists
    >>> raise StockAlreadyExistsError("MSFT")
    StockAlreadyExistsError: Stock with identifier 'MSFT' already exists

    >>> # Invalid symbol
    >>> raise InvalidStockSymbolError("123ABC", "Symbol must contain only letters")
    BusinessRuleViolationError: Business rule 'valid_stock_symbol' violated

    >>> # Invalid grade
    >>> raise InvalidStockGradeError("X", ["A", "B", "C", "D", "F"])
    BusinessRuleViolationError: Business rule 'valid_stock_grade' violated
"""

from typing import Any

from .base import AlreadyExistsError, BusinessRuleViolationError, NotFoundError


class StockNotFoundError(NotFoundError):
    """Exception raised when a stock is not found.

    Specialized version of NotFoundError for stock entities.
    Use this when stock lookup operations fail to find the requested stock.

    When to use:
        - Stock lookup by ID returns None
        - Stock lookup by symbol returns None
        - Attempting operations on non-existent stock

    Example:
        >>> stock = repository.get_by_symbol("AAPL")
        >>> if not stock:
        >>>     raise StockNotFoundError("AAPL")
    """

    def __init__(self, identifier: Any) -> None:
        """Initialize StockNotFoundError.

        Args:
            identifier: The stock ID or symbol that was not found
        """
        super().__init__(entity_type="Stock", identifier=identifier)


class StockAlreadyExistsError(AlreadyExistsError):
    """Exception raised when a stock already exists.

    Specialized version of AlreadyExistsError for stock entities.
    Use this when attempting to create a stock with a duplicate symbol.

    When to use:
        - Creating a stock with an existing symbol
        - Updating a stock symbol to one that's already taken

    Example:
        >>> existing = repository.get_by_symbol("AAPL")
        >>> if existing:
        >>>     raise StockAlreadyExistsError("AAPL")
    """

    def __init__(self, symbol: str) -> None:
        """Initialize StockAlreadyExistsError.

        Args:
            symbol: The stock symbol that already exists
        """
        self.symbol = symbol
        super().__init__(entity_type="Stock", identifier=symbol)


class InvalidStockSymbolError(BusinessRuleViolationError):
    """Exception raised when a stock symbol is invalid.

    Use this exception for stock symbol validation failures.
    Common reasons include invalid format, length, or characters.

    When to use:
        - Symbol contains non-alphabetic characters
        - Symbol is too long or too short
        - Symbol is empty or whitespace only
        - Symbol doesn't meet business format requirements

    Example:
        >>> if not symbol.isalpha():
        >>>     raise InvalidStockSymbolError(
        >>>         symbol="123ABC",
        >>>         reason="Symbol must contain only letters"
        >>>     )

        >>> if len(symbol) > 5:
        >>>     raise InvalidStockSymbolError(
        >>>         symbol=symbol,
        >>>         reason="Symbol must be 5 characters or less"
        >>>     )
    """

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
    """Exception raised when a stock grade is invalid.

    Use this exception when a stock grade doesn't match allowed values.
    Standard grades are A, B, C, D, F, but custom grades can be specified.

    When to use:
        - Grade is not in the allowed list
        - Grade format is invalid
        - Attempting to set an invalid grade

    Example:
        >>> valid_grades = ["A", "B", "C", "D", "F"]
        >>> if grade not in valid_grades:
        >>>     raise InvalidStockGradeError(grade, valid_grades)

        >>> # With custom grades
        >>> custom_grades = ["BUY", "HOLD", "SELL"]
        >>> if grade not in custom_grades:
        >>>     raise InvalidStockGradeError(grade, custom_grades)
    """

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
