"""Base domain exceptions.

This module defines the base exception hierarchy for the domain layer.
All domain-specific exceptions should inherit from these base classes.

Usage Examples:
    Basic usage of base exceptions:

    >>> # Raise a not found error
    >>> raise NotFoundError("Stock", "AAPL")
    NotFoundError: Stock with identifier 'AAPL' not found

    >>> # Raise an already exists error
    >>> raise AlreadyExistsError("Portfolio", "My Portfolio")
    AlreadyExistsError: Portfolio with identifier 'My Portfolio' already exists

    >>> # Raise a business rule violation
    >>> raise BusinessRuleViolationError(
    ...     rule="minimum_portfolio_value",
    ...     context={"value": 100, "minimum": 1000}
    ... )
    BusinessRuleViolationError: Business rule 'minimum_portfolio_value' violated.
        Context: {'value': 100, 'minimum': 1000}
"""

from typing import Any


class DomainError(Exception):
    """Base exception for all domain exceptions.

    This is the root exception class for all domain-specific errors.
    It should be used to catch any domain-related exception when the
    specific type doesn't matter.

    Use this class as a base when creating new domain exception types
    that don't fit into the existing hierarchy.

    Example:
        try:
            # Domain operations
            pass
        except DomainError as e:
            # Handle any domain error
            logger.error(f"Domain error occurred: {e}")
    """


class NotFoundError(DomainError):
    """Exception raised when an entity is not found.

    This exception should be raised when attempting to retrieve or operate on
    an entity that doesn't exist in the system. It's typically mapped to
    HTTP 404 Not Found responses in the presentation layer.

    When to use:
        - Entity lookup by ID returns no results
        - Searching for a unique entity by criteria returns nothing
        - Attempting to update/delete a non-existent entity

    Example:
        >>> # In a repository
        >>> stock = repository.get_by_id(stock_id)
        >>> if not stock:
        >>>     raise NotFoundError("Stock", stock_id)

        >>> # In a service
        >>> portfolio = self.get_portfolio(portfolio_id)
        >>> if not portfolio:
        >>>     raise NotFoundError("Portfolio", portfolio_id)
    """

    def __init__(self, entity_type: str, identifier: Any) -> None:
        """Initialize NotFoundError.

        Args:
            entity_type: The type of entity that was not found
                (e.g., "Stock", "Portfolio")
            identifier: The identifier used to search for the entity
                (ID, symbol, name, etc.)
        """
        self.entity_type = entity_type
        self.identifier = identifier
        super().__init__(self._create_message())

    def _create_message(self) -> str:
        """Create exception message."""
        return f"{self.entity_type} with identifier '{self.identifier}' not found"


class AlreadyExistsError(DomainError):
    """Exception raised when an entity already exists.

    This exception should be raised when attempting to create an entity
    that would violate uniqueness constraints. It's typically mapped to
    HTTP 409 Conflict responses in the presentation layer.

    When to use:
        - Creating an entity with a duplicate unique identifier
        - Adding an entity that violates business uniqueness rules
        - Attempting to rename an entity to a name that's already taken

    Example:
        >>> # In a repository
        >>> existing = repository.get_by_symbol(symbol)
        >>> if existing:
        >>>     raise AlreadyExistsError("Stock", symbol)

        >>> # In a service
        >>> if self.portfolio_exists(name):
        >>>     raise AlreadyExistsError("Portfolio", name)
    """

    def __init__(self, entity_type: str, identifier: Any) -> None:
        """Initialize AlreadyExistsError.

        Args:
            entity_type: The type of entity that already exists
                (e.g., "Stock", "Portfolio")
            identifier: The identifier of the existing entity
                (ID, symbol, name, etc.)
        """
        self.entity_type = entity_type
        self.identifier = identifier
        super().__init__(self._create_message())

    def _create_message(self) -> str:
        """Create exception message."""
        return f"{self.entity_type} with identifier '{self.identifier}' already exists"


class BusinessRuleViolationError(DomainError):
    """Exception raised when a business rule is violated.

    This exception should be raised when an operation would violate
    domain-specific business rules. It's typically mapped to HTTP 422
    Unprocessable Entity responses in the presentation layer.

    When to use:
        - Invalid state transitions (e.g., closing an already closed portfolio)
        - Business logic constraints (e.g., insufficient balance)
        - Domain invariant violations (e.g., negative quantities)
        - Complex validation failures that go beyond simple field validation

    Example:
        >>> # Insufficient balance
        >>> if portfolio.balance < required_amount:
        >>>     raise BusinessRuleViolationError(
        >>>         rule="sufficient_balance",
        >>>         context={
        >>>             "required": required_amount,
        >>>             "available": portfolio.balance
        >>>         }
        >>>     )

        >>> # Invalid state transition
        >>> if portfolio.is_closed:
        >>>     raise BusinessRuleViolationError(
        >>>         rule="portfolio_must_be_active",
        >>>         context={"portfolio_id": portfolio.id, "status": "closed"}
        >>>     )
    """

    def __init__(self, rule: str, context: dict[str, Any] | None = None) -> None:
        """Initialize BusinessRuleViolationError.

        Args:
            rule: The name of the business rule that was violated
                (should be descriptive)
            context: Optional context information about the violation
                (helps with debugging)
        """
        self.rule = rule
        self.context = context
        super().__init__(self._create_message())

    def _create_message(self) -> str:
        """Create exception message."""
        message = f"Business rule '{self.rule}' violated"
        if self.context:
            message += f". Context: {self.context}"
        return message
