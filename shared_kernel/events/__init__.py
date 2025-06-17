"""
Shared event infrastructure used across bounded contexts.

Contains the foundational event system that provides consistent event
handling patterns across all domains.
"""

from .base import DomainEvent

__all__ = ['DomainEvent']