"""
Dependency injection system for StockBook application.

Provides dependency injection container and composition root for clean
architecture dependency management.
"""

from .di_container import DIContainer, RegistrationInfo
from .composition_root import CompositionRoot
from .exceptions import (
    DependencyInjectionError,
    DependencyResolutionError,
    CircularDependencyError,
    DuplicateRegistrationError,
    InvalidRegistrationError
)
from .lifetimes import Lifetime

__all__ = [
    'DIContainer',
    'RegistrationInfo', 
    'CompositionRoot',
    'DependencyInjectionError',
    'DependencyResolutionError',
    'CircularDependencyError',
    'DuplicateRegistrationError',
    'InvalidRegistrationError',
    'Lifetime'
]