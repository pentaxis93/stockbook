"""
Unit tests for dependency injection container.

Following TDD approach - these tests define the expected behavior
of our DI container before implementation.
"""

from abc import ABC, abstractmethod
from typing import Optional

import pytest

# These imports now exist after implementation
from dependency_injection.di_container import DIContainer
from dependency_injection.exceptions import (
    CircularDependencyError,
    DependencyResolutionError,
    DuplicateRegistrationError,
)
from dependency_injection.lifetimes import Lifetime


# Test interfaces and classes for DI testing
class ITestRepository(ABC):
    @abstractmethod
    def get_data(self) -> str:
        pass


class MockTestRepository(ITestRepository):
    def get_data(self) -> str:
        return "test_data"


class MockTestService:
    def __init__(self, repository: ITestRepository):
        self.repository = repository

    def process(self) -> str:
        return f"processed_{self.repository.get_data()}"


class MockTestController:
    def __init__(self, service: MockTestService):
        self.service = service

    def handle_request(self) -> str:
        return f"handled_{self.service.process()}"


# Circular dependency test classes
class MockServiceA:
    def __init__(self, service_b: "MockServiceB"):
        self.service_b = service_b


class MockServiceB:
    def __init__(self, service_a: MockServiceA):
        self.service_a = service_a


class MockSimpleService:
    """Service with no dependencies."""

    def __init__(self):
        self.value = "simple"


class MockServiceWithOptionalDep:
    """Service with optional dependency (default parameter)."""

    def __init__(self, repository: Optional[ITestRepository] = None):
        self.repository = repository


class TestDIContainerBasics:
    """Test basic DI container functionality."""

    def setup_method(self) -> None:
        """Create fresh container for each test."""
        self.container = DIContainer()

    def test_register_and_resolve_singleton(self) -> None:
        """Should register singleton and return same instance."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestRepository, MockTestRepository)

        # Act
        instance1 = container.resolve(ITestRepository)
        instance2 = container.resolve(ITestRepository)

        # Assert
        assert instance1 is instance2
        assert isinstance(instance1, MockTestRepository)

    def test_register_and_resolve_transient(self) -> None:
        """Should create new instance each time for transient."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestRepository, MockTestRepository)
        container.register_transient(MockTestService)

        # Act
        instance1 = container.resolve(MockTestService)
        instance2 = container.resolve(MockTestService)

        # Assert
        assert instance1 is not instance2
        assert isinstance(instance1, MockTestService)
        assert isinstance(instance2, MockTestService)

    def test_register_instance(self) -> None:
        """Should register and resolve pre-created instances."""
        # Arrange
        container = DIContainer()
        instance = MockTestRepository()
        container.register_instance(ITestRepository, instance)

        # Act
        resolved = container.resolve(ITestRepository)

        # Assert
        assert resolved is instance

    def test_register_factory(self) -> None:
        """Should register and use factory functions."""
        # Arrange
        container = DIContainer()

        def create_repository() -> ITestRepository:
            return MockTestRepository()

        container.register_factory(ITestRepository, create_repository)

        # Act
        resolved = container.resolve(ITestRepository)

        # Assert
        assert isinstance(resolved, MockTestRepository)


class TestDependencyInjection:
    """Test automatic dependency injection."""

    def test_simple_dependency_injection(self) -> None:
        """Should automatically inject constructor dependencies."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestRepository, MockTestRepository)
        container.register_transient(MockTestService)

        # Act
        service = container.resolve(MockTestService)

        # Assert
        assert isinstance(service.repository, MockTestRepository)
        assert service.process() == "processed_test_data"

    def test_nested_dependency_resolution(self) -> None:
        """Should resolve complex dependency chains."""
        # Arrange - MockTestController -> MockTestService -> ITestRepository
        container = DIContainer()
        container.register_singleton(ITestRepository, MockTestRepository)
        container.register_transient(MockTestService)
        container.register_transient(MockTestController)

        # Act
        controller = container.resolve(MockTestController)

        # Assert
        assert isinstance(controller.service, MockTestService)
        assert isinstance(controller.service.repository, MockTestRepository)
        assert controller.handle_request() == "handled_processed_test_data"

    def test_no_dependencies_service(self) -> None:
        """Should handle classes with no dependencies."""
        # Arrange
        container = DIContainer()
        container.register_transient(MockSimpleService)

        # Act
        service = container.resolve(MockSimpleService)

        # Assert
        assert isinstance(service, MockSimpleService)
        assert service.value == "simple"

    def test_interface_to_implementation_resolution(self) -> None:
        """Should resolve interface types to concrete implementations."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestRepository, MockTestRepository)

        # Act
        resolved = container.resolve(ITestRepository)

        # Assert
        assert isinstance(resolved, MockTestRepository)
        assert isinstance(resolved, ITestRepository)


class TestLifetimeManagement:
    """Test different dependency lifetime management."""

    def test_singleton_lifecycle(self) -> None:
        """Should create and reuse singleton instances."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestRepository, MockTestRepository)

        # Act
        instance1 = container.resolve(ITestRepository)
        instance2 = container.resolve(ITestRepository)
        instance3 = container.resolve(ITestRepository)

        # Assert
        assert instance1 is instance2 is instance3

    def test_transient_lifecycle(self) -> None:
        """Should create new transient instances."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestRepository, MockTestRepository)
        container.register_transient(MockTestService)

        # Act
        instance1 = container.resolve(MockTestService)
        instance2 = container.resolve(MockTestService)
        instance3 = container.resolve(MockTestService)

        # Assert
        assert instance1 is not instance2
        assert instance2 is not instance3
        assert instance1 is not instance3

    def test_mixed_lifetimes(self) -> None:
        """Should handle mixed singleton and transient lifetimes correctly."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestRepository, MockTestRepository)  # Singleton
        container.register_transient(MockTestService)  # Transient, depends on singleton

        # Act
        service1 = container.resolve(MockTestService)
        service2 = container.resolve(MockTestService)

        # Assert
        assert service1 is not service2  # Different services
        assert service1.repository is service2.repository  # Same repository


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_unregistered_dependency_error(self) -> None:
        """Should raise clear error for unregistered types."""
        # Arrange
        container = DIContainer()

        # Act & Assert
        with pytest.raises(DependencyResolutionError) as exc_info:
            _ = container.resolve(MockTestService)  # Missing ITestRepository
        assert "MockTestService" in str(exc_info.value)
        assert "not registered" in str(exc_info.value)

    def test_circular_dependency_detection(self) -> None:
        """Should detect and prevent circular dependencies."""
        # Arrange
        container = DIContainer()
        container.register_transient(MockServiceA)
        container.register_transient(MockServiceB)

        # Act & Assert
        with pytest.raises(CircularDependencyError) as exc_info:
            _ = container.resolve(MockServiceA)
        assert "circular dependency" in str(exc_info.value).lower()
        assert "MockServiceA" in str(exc_info.value)
        assert "MockServiceB" in str(exc_info.value)

    def test_resolve_nonexistent_type(self) -> None:
        """Should raise clear error for completely unregistered type."""
        # Arrange
        container = DIContainer()

        # Act & Assert
        with pytest.raises(DependencyResolutionError) as exc_info:
            _ = container.resolve(MockTestRepository)
        assert "MockTestRepository" in str(exc_info.value)
        assert "not registered" in str(exc_info.value)

    def test_register_same_type_twice_error(self) -> None:
        """Should handle re-registration attempts clearly."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestRepository, MockTestRepository)

        # Act & Assert - should error on duplicate registration
        with pytest.raises(DuplicateRegistrationError):
            container.register_singleton(ITestRepository, MockTestRepository)


class TestContainerIntrospection:
    """Test container introspection capabilities."""

    def test_is_registered(self) -> None:
        """Should check if type is registered."""
        container = DIContainer()
        assert not container.is_registered(ITestRepository)

        container.register_singleton(ITestRepository, MockTestRepository)
        assert container.is_registered(ITestRepository)

    def test_get_registrations(self) -> None:
        """Should list all registered types."""
        container = DIContainer()
        container.register_singleton(ITestRepository, MockTestRepository)
        container.register_transient(MockTestService)

        registrations = container.get_registrations()
        assert len(registrations) == 2
        assert ITestRepository in registrations
        assert MockTestService in registrations

    def test_registration_info(self) -> None:
        """Should provide registration details."""
        container = DIContainer()
        container.register_singleton(ITestRepository, MockTestRepository)

        info = container.get_registration_info(ITestRepository)
        assert info is not None
        assert info.service_type == ITestRepository
        assert info.implementation_type == MockTestRepository
        assert info.lifetime == Lifetime.SINGLETON
