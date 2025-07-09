"""Domain exceptions module.

This module provides a comprehensive exception hierarchy for the StockBook domain layer.
All domain-specific exceptions are available through this single import point.

Import Examples:
    >>> # Import all exceptions
    >>> from src.domain.exceptions import *

    >>> # Import specific exceptions
    >>> from src.domain.exceptions import (
    ...     StockNotFoundError,
    ...     PortfolioBalanceError,
    ...     BusinessRuleViolationError
    ... )

    >>> # Import from parent domain module
    >>> from src.domain import StockNotFoundError, PortfolioNotFoundError

Exception Hierarchy:
    DomainError (base for all domain exceptions)
    ├── NotFoundError (entity not found)
    │   ├── StockNotFoundError
    │   └── PortfolioNotFoundError
    ├── AlreadyExistsError (duplicate entity)
    │   ├── StockAlreadyExistsError
    │   └── PortfolioAlreadyExistsError
    └── BusinessRuleViolationError (business logic violations)
        ├── InvalidStockSymbolError
        ├── InvalidStockGradeError
        ├── InactivePortfolioError
        └── PortfolioBalanceError

Usage Patterns:
    1. Catch all domain errors:
        try:
            service.execute_operation()
        except DomainError as e:
            logger.error(f"Domain error: {e}")

    2. Catch specific error types:
        try:
            stock = service.get_stock(symbol)
        except StockNotFoundError:
            return None
        except StockAlreadyExistsError:
            return existing_stock

    3. Handle business rule violations:
        try:
            portfolio.withdraw(amount)
        except PortfolioBalanceError as e:
            req, avail = e.required_amount, e.available_amount
            return f"Insufficient funds: need {req}, have {avail}"
"""

from .base import (
    AlreadyExistsError,
    BusinessRuleViolationError,
    DomainError,
    NotFoundError,
)
from .portfolio import (
    InactivePortfolioError,
    PortfolioAlreadyExistsError,
    PortfolioBalanceError,
    PortfolioNotFoundError,
)
from .stock import (
    InvalidStockGradeError,
    InvalidStockSymbolError,
    StockAlreadyExistsError,
    StockNotFoundError,
)

__all__ = [
    "AlreadyExistsError",
    "BusinessRuleViolationError",
    "DomainError",
    "InactivePortfolioError",
    "InvalidStockGradeError",
    "InvalidStockSymbolError",
    "NotFoundError",
    "PortfolioAlreadyExistsError",
    "PortfolioBalanceError",
    "PortfolioNotFoundError",
    "StockAlreadyExistsError",
    "StockNotFoundError",
]
