"""Portfolio-specific domain exceptions.

This module defines exceptions specific to portfolio-related operations.
These exceptions handle portfolio lifecycle, balance, and state violations.

Usage Examples:
    >>> # Portfolio not found
    >>> raise PortfolioNotFoundError("portfolio-123")
    PortfolioNotFoundError: Portfolio with identifier 'portfolio-123' not found

    >>> # Portfolio already exists
    >>> raise PortfolioAlreadyExistsError("My Portfolio")
    PortfolioAlreadyExistsError: Portfolio with identifier 'My Portfolio' already exists

    >>> # Inactive portfolio
    >>> raise InactivePortfolioError(
    ...     portfolio_id="portfolio-1",
    ...     operation="add_position",
    ...     portfolio_name="Retired Portfolio"
    ... )
    BusinessRuleViolationError: Business rule 'portfolio_must_be_active' violated

    >>> # Insufficient balance
    >>> raise PortfolioBalanceError(
    ...     portfolio_id="portfolio-1",
    ...     required_amount=1000.0,
    ...     available_amount=500.0,
    ...     operation="buy_stock"
    ... )
    BusinessRuleViolationError: Business rule 'sufficient_portfolio_balance' violated
"""

from typing import Any

from .base import AlreadyExistsError, BusinessRuleViolationError, NotFoundError


class PortfolioNotFoundError(NotFoundError):
    """Exception raised when a portfolio is not found.

    Specialized version of NotFoundError for portfolio entities.
    Use this when portfolio lookup operations fail to find the requested portfolio.

    When to use:
        - Portfolio lookup by ID returns None
        - Portfolio lookup by name returns None
        - Attempting operations on non-existent portfolio

    Example:
        >>> portfolio = repository.get_by_id(portfolio_id)
        >>> if not portfolio:
        >>>     raise PortfolioNotFoundError(portfolio_id)
    """

    def __init__(self, identifier: Any) -> None:
        """Initialize PortfolioNotFoundError.

        Args:
            identifier: The portfolio ID or name that was not found
        """
        super().__init__(entity_type="Portfolio", identifier=identifier)


class PortfolioAlreadyExistsError(AlreadyExistsError):
    """Exception raised when a portfolio already exists.

    Specialized version of AlreadyExistsError for portfolio entities.
    Use this when attempting to create a portfolio with a duplicate name.

    When to use:
        - Creating a portfolio with an existing name
        - Renaming a portfolio to a name that's already taken

    Example:
        >>> existing = repository.get_by_name("My Portfolio")
        >>> if existing:
        >>>     raise PortfolioAlreadyExistsError("My Portfolio")
    """

    def __init__(self, name: str) -> None:
        """Initialize PortfolioAlreadyExistsError.

        Args:
            name: The portfolio name that already exists
        """
        self.name = name
        super().__init__(entity_type="Portfolio", identifier=name)


class InactivePortfolioError(BusinessRuleViolationError):
    """Exception raised when attempting operations on an inactive portfolio.

    Use this exception when trying to modify or perform transactions
    on a portfolio that has been closed, archived, or otherwise deactivated.

    When to use:
        - Adding positions to a closed portfolio
        - Executing trades on an archived portfolio
        - Modifying settings of an inactive portfolio
        - Any write operation on a non-active portfolio

    Example:
        >>> if portfolio.status != "active":
        >>>     raise InactivePortfolioError(
        >>>         portfolio_id=portfolio.id,
        >>>         operation="add_position",
        >>>         portfolio_name=portfolio.name
        >>>     )
    """

    def __init__(
        self,
        portfolio_id: str,
        operation: str = "modify",
        portfolio_name: str | None = None,
    ) -> None:
        """Initialize InactivePortfolioError.

        Args:
            portfolio_id: The ID of the inactive portfolio
            operation: The operation being attempted (default: "modify")
            portfolio_name: Optional name of the portfolio
        """
        self.portfolio_id = portfolio_id
        self.portfolio_name = portfolio_name
        context = {
            "portfolio_id": portfolio_id,
            "operation": operation,
        }
        if portfolio_name:
            context["portfolio_name"] = portfolio_name
        super().__init__(rule="portfolio_must_be_active", context=context)


class PortfolioBalanceError(BusinessRuleViolationError):
    """Exception raised when portfolio has insufficient balance.

    Use this exception when a portfolio doesn't have enough available
    funds to complete a requested operation.

    When to use:
        - Buying stocks with insufficient cash
        - Withdrawing more than available balance
        - Transaction would result in negative balance
        - Any operation requiring more funds than available

    Example:
        >>> cost = shares * price
        >>> if portfolio.cash_balance < cost:
        >>>     raise PortfolioBalanceError(
        >>>         portfolio_id=portfolio.id,
        >>>         required_amount=cost,
        >>>         available_amount=portfolio.cash_balance,
        >>>         operation="buy_stock"
        >>>     )
    """

    def __init__(
        self,
        portfolio_id: str,
        required_amount: float,
        available_amount: float,
        operation: str | None = None,
    ) -> None:
        """Initialize PortfolioBalanceError.

        Args:
            portfolio_id: The ID of the portfolio with insufficient balance
            required_amount: The amount required for the operation
            available_amount: The amount available in the portfolio
            operation: Optional operation being attempted
        """
        self.portfolio_id = portfolio_id
        self.required_amount = required_amount
        self.available_amount = available_amount
        context = {
            "portfolio_id": portfolio_id,
            "required_amount": required_amount,
            "available_amount": available_amount,
            "shortfall": required_amount - available_amount,
        }
        if operation:
            context["operation"] = operation
        super().__init__(rule="sufficient_portfolio_balance", context=context)
