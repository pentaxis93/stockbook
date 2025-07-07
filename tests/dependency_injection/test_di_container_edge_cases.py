"""
Unit tests for edge cases and error conditions in DI container.

Tests exception handling and other edge cases not covered in main tests.
"""

from unittest.mock import patch

import pytest

from dependency_injection.di_container import DIContainer
from dependency_injection.exceptions import (
    DuplicateRegistrationError,
    InvalidRegistrationError,
)


class MockService:
    """Mock service for testing."""


class MockImplementation(MockService):
    """Mock implementation for testing."""

    def __init__(self) -> None:
        super().__init__()


class NotAService:
    """Class that doesn't implement MockService."""


class TestRegistrationExceptions:
    """Test exception handling during registration."""

    def test_singleton_registration_exception_handling(self) -> None:
        """Should handle exceptions during singleton registration."""
        container = DIContainer()

        # Mock the provider creation to raise an exception
        with patch(
            "dependency_injection.di_container.providers.Singleton"
        ) as mock_provider:
            mock_provider.side_effect = Exception("Provider creation failed")

            with pytest.raises(InvalidRegistrationError) as exc_info:
                container.register_singleton(MockService, MockImplementation)

            assert "Failed to register singleton" in str(exc_info.value)
            assert "Provider creation failed" in str(exc_info.value)

    def test_transient_registration_exception_handling(self) -> None:
        """Should handle exceptions during transient registration."""
        container = DIContainer()

        # Mock the provider creation to raise an exception
        with patch(
            "dependency_injection.di_container.providers.Factory"
        ) as mock_provider:
            mock_provider.side_effect = Exception("Factory creation failed")

            with pytest.raises(InvalidRegistrationError) as exc_info:
                container.register_transient(MockService, MockImplementation)

            assert "Failed to register transient" in str(exc_info.value)
            assert "Factory creation failed" in str(exc_info.value)

    def test_instance_registration_exception_handling(self) -> None:
        """Should handle exceptions during instance registration."""
        container = DIContainer()
        instance = MockImplementation()

        # Mock the provider creation to raise an exception
        with patch(
            "dependency_injection.di_container.providers.Object"
        ) as mock_provider:
            mock_provider.side_effect = Exception("Object provider failed")

            with pytest.raises(InvalidRegistrationError) as exc_info:
                container.register_instance(MockService, instance)

            assert "Failed to register instance" in str(exc_info.value)
            assert "Object provider failed" in str(exc_info.value)

    def test_factory_registration_exception_handling(self) -> None:
        """Should handle exceptions during factory registration."""
        container = DIContainer()

        def factory() -> MockService:
            return MockImplementation()

        # Mock the provider creation to raise an exception
        with patch(
            "dependency_injection.di_container.providers.Callable"
        ) as mock_provider:
            mock_provider.side_effect = Exception("Callable provider failed")

            with pytest.raises(InvalidRegistrationError) as exc_info:
                container.register_factory(MockService, factory)

            assert "Failed to register factory" in str(exc_info.value)
            assert "Callable provider failed" in str(exc_info.value)

    def test_duplicate_transient_registration_error(self) -> None:
        """Should raise error when registering duplicate transient."""
        container = DIContainer()
        container.register_transient(MockService)

        with pytest.raises(DuplicateRegistrationError) as exc_info:
            container.register_transient(MockService)

        assert "MockService is already registered" in str(exc_info.value)

    def test_duplicate_instance_registration_error(self) -> None:
        """Should raise error when registering duplicate instance."""
        container = DIContainer()
        instance = MockImplementation()
        container.register_instance(MockService, instance)

        with pytest.raises(DuplicateRegistrationError) as exc_info:
            container.register_instance(MockService, instance)

        assert "MockService is already registered" in str(exc_info.value)

    def test_duplicate_factory_registration_error(self) -> None:
        """Should raise error when registering duplicate factory."""
        container = DIContainer()

        def factory() -> MockService:
            return MockImplementation()

        container.register_factory(MockService, factory)

        with pytest.raises(DuplicateRegistrationError) as exc_info:
            container.register_factory(MockService, factory)

        assert "MockService is already registered" in str(exc_info.value)

    def test_incompatible_instance_registration(self) -> None:
        """Should raise error when instance doesn't match service type."""
        container = DIContainer()
        wrong_instance = NotAService()

        with pytest.raises(InvalidRegistrationError) as exc_info:
            container.register_instance(MockService, wrong_instance)

        assert "NotAService is not compatible with service type MockService" in str(
            exc_info.value
        )


class TestValidationEdgeCases:
    """Test edge cases in validation logic."""

    def test_validate_incompatible_abstract_implementation(self) -> None:
        """Should reject implementations that don't implement abstract interface."""
        from abc import ABC, abstractmethod

        class IAbstractService(ABC):
            @abstractmethod
            def method(self) -> None:
                pass

        class WrongImplementation:
            """Doesn't inherit from IAbstractService."""

            def other_method(self) -> None:
                pass

        container = DIContainer()

        with pytest.raises(InvalidRegistrationError) as exc_info:
            container.register_singleton(IAbstractService, WrongImplementation)

        assert (
            "WrongImplementation does not implement interface IAbstractService"
            in str(exc_info.value)
        )

    def test_validate_non_class_implementation(self) -> None:
        """Should reject non-class implementations."""
        container = DIContainer()

        def not_a_class() -> None:
            pass

        with pytest.raises(InvalidRegistrationError) as exc_info:
            container.register_singleton(MockService, not_a_class)  # type: ignore[arg-type]

        assert "is not a class" in str(exc_info.value)


class TestResolutionEdgeCases:
    """Test edge cases during resolution."""

    def test_constructor_with_no_dependencies(self) -> None:
        """Should handle classes with no constructor dependencies."""

        class NoDependencyService:
            def __init__(self) -> None:
                self.value = "created"

        container = DIContainer()
        container.register_transient(NoDependencyService)

        # Should create it without any dependency injection
        instance = container.resolve(NoDependencyService)
        assert isinstance(instance, NoDependencyService)
        assert instance.value == "created"


class TestContainerState:
    """Test container state management."""

    def test_get_registration_info_not_found(self) -> None:
        """Should return None for unregistered types."""
        container = DIContainer()
        info = container.get_registration_info(MockService)
        assert info is None

    def test_container_state_after_failed_registration(self) -> None:
        """Container state should be consistent after failed registration."""
        container = DIContainer()

        # Try to register with an error
        with patch(
            "dependency_injection.di_container.providers.Singleton"
        ) as mock_provider:
            mock_provider.side_effect = Exception("Failed")

            with pytest.raises(InvalidRegistrationError):
                container.register_singleton(MockService)

        # Container should not have the failed registration
        assert not container.is_registered(MockService)
        assert MockService not in container.get_registrations()
