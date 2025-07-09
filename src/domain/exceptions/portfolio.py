"""Portfolio-specific domain exceptions."""

from typing import Any

from .base import AlreadyExistsError, BusinessRuleViolationError, NotFoundError


class PortfolioNotFoundError(NotFoundError):
    """Exception raised when a portfolio is not found."""

    def __init__(self, identifier: Any) -> None:
        """Initialize PortfolioNotFoundError.

        Args:
            identifier: The portfolio ID or name that was not found
        """
        super().__init__(entity_type="Portfolio", identifier=identifier)


class PortfolioAlreadyExistsError(AlreadyExistsError):
    """Exception raised when a portfolio already exists."""

    def __init__(self, name: str) -> None:
        """Initialize PortfolioAlreadyExistsError.

        Args:
            name: The portfolio name that already exists
        """
        self.name = name
        super().__init__(entity_type="Portfolio", identifier=name)


class InactivePortfolioError(BusinessRuleViolationError):
    """Exception raised when attempting operations on an inactive portfolio."""

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
    """Exception raised when portfolio has insufficient balance."""

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
