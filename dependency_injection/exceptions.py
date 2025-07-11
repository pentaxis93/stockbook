"""Dependency injection exceptions.

Provides clear, helpful error messages for common DI configuration
and usage mistakes.
"""

from typing import Any


class DependencyInjectionError(Exception):
    """Base exception for all dependency injection errors."""


class DependencyResolutionError(DependencyInjectionError):
    """Raised when a dependency cannot be resolved."""

    def __init__(
        self,
        service_type: type[Any],
        message: str,
        resolution_chain: list[str] | None = None,
    ) -> None:
        """Initialize dependency resolution error with details."""
        self.service_type = service_type
        self.resolution_chain = resolution_chain or []
        super().__init__(message)

    def __str__(self) -> str:
        base_message = super().__str__()
        if self.resolution_chain:
            chain_str = " -> ".join(self.resolution_chain)
            return f"{base_message} (Resolution chain: {chain_str})"
        return base_message


class CircularDependencyError(DependencyInjectionError):
    """Raised when a circular dependency is detected."""

    def __init__(self, dependency_chain: list[str]) -> None:
        """Initialize circular dependency error with the dependency chain."""
        self.dependency_chain = dependency_chain
        chain_str = " -> ".join(dependency_chain)
        message = f"Circular dependency detected: {chain_str}"
        super().__init__(message)


class DuplicateRegistrationError(DependencyInjectionError):
    """Raised when attempting to register a service that's already registered."""

    def __init__(self, service_type: type[Any], message: str) -> None:
        """Initialize duplicate registration error."""
        self.service_type = service_type
        super().__init__(message)


class InvalidRegistrationError(DependencyInjectionError):
    """Raised when registration parameters are invalid."""

    def __init__(self, service_type: type[Any], message: str) -> None:
        """Initialize invalid registration error."""
        self.service_type = service_type
        super().__init__(message)
