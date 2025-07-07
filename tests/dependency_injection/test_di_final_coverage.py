"""Final coverage test for dependency injection."""

import pytest
from dependency_injector.errors import Error as DIError

from dependency_injection.di_container import DIContainer
from dependency_injection.exceptions import DependencyResolutionError


class FailingService:
    """Service that fails during injection."""

    def __init__(self) -> None:
        msg = "Injection failed during construction"
        raise DIError(msg)


def test_provider_di_error_wrapped() -> None:
    """Test that DIError from provider is properly wrapped."""
    container = DIContainer()

    # Register a service that will fail with DIError during construction
    container.register_transient(FailingService)

    # When we try to resolve it, the DIError should be caught and wrapped
    with pytest.raises(DependencyResolutionError) as exc_info:
        _ = container.resolve(FailingService)

    # Check that the error was properly wrapped
    assert "Failed to resolve FailingService" in str(exc_info.value)
    assert "Injection failed during construction" in str(exc_info.value)
