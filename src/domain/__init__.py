"""Domain layer for StockBook application.

This layer contains the core business logic and rules,
independent of external concerns like databases or UI frameworks.
"""

# Re-export all domain exceptions for convenience
from .exceptions import (
    AlreadyExistsError,
    BusinessRuleViolationError,
    DomainError,
    InactivePortfolioError,
    InvalidStockGradeError,
    InvalidStockSymbolError,
    NotFoundError,
    PortfolioAlreadyExistsError,
    PortfolioBalanceError,
    PortfolioNotFoundError,
    StockAlreadyExistsError,
    StockNotFoundError,
)

__all__ = [
    "AlreadyExistsError",
    "BusinessRuleViolationError",
    # Base exceptions
    "DomainError",
    "InactivePortfolioError",
    "InvalidStockGradeError",
    "InvalidStockSymbolError",
    "NotFoundError",
    "PortfolioAlreadyExistsError",
    "PortfolioBalanceError",
    # Portfolio exceptions
    "PortfolioNotFoundError",
    "StockAlreadyExistsError",
    # Stock exceptions
    "StockNotFoundError",
]
