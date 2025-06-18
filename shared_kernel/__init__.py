"""
Shared Kernel - Common components across bounded contexts.

The shared kernel contains foundational components that are reused across
multiple bounded contexts in the stockbook application. This includes:

- Common value objects (Money, Quantity)
- Base domain events infrastructure
- Common domain exceptions
- Common interfaces (Unit of Work pattern)

These components follow domain-driven design principles and are designed
to be stable, well-tested, and reusable across different domains.
"""

# Domain Events
from .events import DomainEvent

# Domain Exceptions
from .exceptions import (
    AnalysisError,
    BusinessRuleViolationError,
    CalculationError,
    DomainServiceError,
    InsufficientDataError,
    ValidationError,
)

# Interfaces
from .interfaces import IUnitOfWork

# Value Objects
from .value_objects import Money, Quantity

__all__ = [
    # Value Objects
    "Money",
    "Quantity",
    # Domain Events
    "DomainEvent",
    # Domain Exceptions
    "DomainServiceError",
    "ValidationError",
    "BusinessRuleViolationError",
    "CalculationError",
    "InsufficientDataError",
    "AnalysisError",
    # Interfaces
    "IUnitOfWork",
]
