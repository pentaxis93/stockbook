"""
Shared value objects used across bounded contexts.

Contains foundational value objects like Money and Quantity that provide
building blocks for any financial or business domain.
"""

from .money import Money
from .quantity import Quantity

__all__ = ['Money', 'Quantity']