"""Base domain exceptions."""

from typing import Any


class DomainError(Exception):
    """Base exception for all domain exceptions."""


class NotFoundError(DomainError):
    """Exception raised when an entity is not found."""

    def __init__(self, entity_type: str, identifier: Any) -> None:
        """Initialize NotFoundError.

        Args:
            entity_type: The type of entity that was not found
            identifier: The identifier used to search for the entity
        """
        self.entity_type = entity_type
        self.identifier = identifier
        super().__init__(self._create_message())

    def _create_message(self) -> str:
        """Create exception message."""
        return f"{self.entity_type} with identifier '{self.identifier}' not found"


class AlreadyExistsError(DomainError):
    """Exception raised when an entity already exists."""

    def __init__(self, entity_type: str, identifier: Any) -> None:
        """Initialize AlreadyExistsError.

        Args:
            entity_type: The type of entity that already exists
            identifier: The identifier of the existing entity
        """
        self.entity_type = entity_type
        self.identifier = identifier
        super().__init__(self._create_message())

    def _create_message(self) -> str:
        """Create exception message."""
        return f"{self.entity_type} with identifier '{self.identifier}' already exists"


class BusinessRuleViolationError(DomainError):
    """Exception raised when a business rule is violated."""

    def __init__(self, rule: str, context: dict[str, Any] | None = None) -> None:
        """Initialize BusinessRuleViolationError.

        Args:
            rule: The name of the business rule that was violated
            context: Optional context information about the violation
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
