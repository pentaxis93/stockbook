"""
Shared Kernel - Common components across bounded contexts.

The shared kernel contains foundational components that are reused across
multiple bounded contexts in the stockbook application. This includes:

- Base domain events infrastructure

These components follow domain-driven design principles and are designed
to be stable, well-tested, and reusable across different domains.

Note: Value objects (Money, Quantity), domain exceptions, and interfaces
have been moved to src.domain.* for single-context thinking approach.
"""

# Domain Events
from src.domain.events.base import DomainEvent

__all__ = [
    # Domain Events
    "DomainEvent",
]
