"""
Tests for missing coverage in DI container.
"""

from typing import TYPE_CHECKING, Any

import pytest

from dependency_injection.di_container import DIContainer
from dependency_injection.exceptions import (
    DependencyResolutionError,
    InvalidRegistrationError,
)

if TYPE_CHECKING:
    UnknownService = Any


class MockService:
    """Mock service for testing."""


def test_non_callable_factory_error() -> None:
    """Should raise error when factory is not callable."""
    container = DIContainer()
    not_callable = "not a function"  # String is not callable

    with pytest.raises(InvalidRegistrationError) as exc_info:
        container.register_factory(MockService, not_callable)  # type: ignore[arg-type]

    assert "Factory for MockService is not callable" in str(exc_info.value)


def test_forward_reference_not_found() -> None:
    """Should raise error when forward reference cannot be resolved."""

    class ServiceWithForwardRef:
        def __init__(self, dependency: "UnknownService") -> None:
            self.dependency = dependency

    container = DIContainer()
    container.register_transient(ServiceWithForwardRef)

    # Try to resolve - will fail because UnknownService is not registered
    with pytest.raises(DependencyResolutionError) as exc_info:
        _ = container.resolve(ServiceWithForwardRef)

    assert "No registered type found for forward reference 'UnknownService'" in str(
        exc_info.value,
    )
