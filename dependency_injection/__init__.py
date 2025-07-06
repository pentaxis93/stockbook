"""Dependency injection system for StockBook application.

Provides dependency injection container and composition root for clean
architecture dependency management.
"""

from .composition_root import CompositionRoot
from .di_container import DIContainer, RegistrationInfo
from .exceptions import (
    CircularDependencyError,
    DependencyInjectionError,
    DependencyResolutionError,
    DuplicateRegistrationError,
    InvalidRegistrationError,
)
from .lifetimes import Lifetime

__all__ = [
    "CircularDependencyError",
    "CompositionRoot",
    "DIContainer",
    "DependencyInjectionError",
    "DependencyResolutionError",
    "DuplicateRegistrationError",
    "InvalidRegistrationError",
    "Lifetime",
    "RegistrationInfo",
]
