"""
Shared interfaces used across bounded contexts.

Contains foundational interfaces that provide consistent contracts
across all domains for infrastructure concerns.
"""

from .unit_of_work import IUnitOfWork

__all__ = ["IUnitOfWork"]
