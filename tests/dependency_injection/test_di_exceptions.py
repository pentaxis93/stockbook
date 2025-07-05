"""
Unit tests for dependency injection exceptions.

Tests that DI system provides clear, helpful error messages
for common configuration and usage mistakes.
"""

from dependency_injection.exceptions import (
    CircularDependencyError,
    DependencyInjectionError,
    DependencyResolutionError,
    DuplicateRegistrationError,
    InvalidRegistrationError,
)


class MockService:
    """Mock service for testing."""

    pass


class TestDependencyResolutionError:
    """Test dependency resolution error messages."""

    def test_basic_error_message(self) -> None:
        """Should create error with basic message."""
        error = DependencyResolutionError(
            MockService, "MockService is not registered in the container"
        )

        assert "MockService is not registered" in str(error)
        assert error.service_type == MockService
        assert isinstance(error, DependencyInjectionError)

    def test_error_with_resolution_chain(self) -> None:
        """Should show resolution chain in error messages."""
        error = DependencyResolutionError(
            MockService,
            "Cannot resolve dependency",
            resolution_chain=["ControllerA", "ServiceB", "RepositoryC"],
        )

        error_str = str(error)
        assert "Cannot resolve dependency" in error_str
        assert "Resolution chain: ControllerA -> ServiceB -> RepositoryC" in error_str
        assert error.resolution_chain == ["ControllerA", "ServiceB", "RepositoryC"]

    def test_error_without_resolution_chain(self) -> None:
        """Should handle error without resolution chain."""
        error = DependencyResolutionError(MockService, "Simple error message")

        assert str(error) == "Simple error message"
        assert error.resolution_chain == []


class TestCircularDependencyError:
    """Test circular dependency detection and error messages."""

    def test_simple_circular_dependency_error(self) -> None:
        """Should detect A -> B -> A circular dependency."""
        error = CircularDependencyError(["ServiceA", "ServiceB", "ServiceA"])

        error_str = str(error).lower()
        assert "circular dependency detected" in error_str
        assert "servicea -> serviceb -> servicea" in error_str
        assert error.dependency_chain == ["ServiceA", "ServiceB", "ServiceA"]
        assert isinstance(error, DependencyInjectionError)

    def test_complex_circular_dependency_error(self) -> None:
        """Should detect longer circular dependency chains."""
        chain = ["ServiceA", "ServiceB", "ServiceC", "ServiceD", "ServiceB"]
        error = CircularDependencyError(chain)

        assert "ServiceA -> ServiceB -> ServiceC -> ServiceD -> ServiceB" in str(error)
        assert error.dependency_chain == chain

    def test_self_circular_dependency_error(self) -> None:
        """Should detect self-referencing circular dependencies."""
        error = CircularDependencyError(["SelfService", "SelfService"])

        error_str = str(error)
        assert "SelfService -> SelfService" in error_str
        assert "Circular dependency detected" in error_str


class TestDuplicateRegistrationError:
    """Test duplicate registration handling."""

    def test_duplicate_registration_error_message(self) -> None:
        """Should provide clear message for duplicate registrations."""
        error = DuplicateRegistrationError(
            MockService,
            "MockService is already registered. Use replace=True to override.",
        )

        error_str = str(error)
        assert "MockService is already registered" in error_str
        assert "replace=True" in error_str
        assert error.service_type == MockService
        assert isinstance(error, DependencyInjectionError)

    def test_duplicate_with_different_implementation_error(self) -> None:
        """Should show what was previously registered."""
        error = DuplicateRegistrationError(
            MockService,
            "MockService is already registered as ServiceImpl, cannot register as AnotherImpl",
        )

        error_str = str(error)
        assert "ServiceImpl" in error_str
        assert "AnotherImpl" in error_str


class TestInvalidRegistrationError:
    """Test invalid registration scenarios."""

    def test_invalid_implementation_type_error(self) -> None:
        """Should validate implementation type matches interface."""
        error = InvalidRegistrationError(
            MockService, "TestRepository does not implement MockService"
        )

        error_str = str(error)
        assert "does not implement" in error_str
        assert "MockService" in error_str
        assert "TestRepository" in error_str
        assert error.service_type == MockService
        assert isinstance(error, DependencyInjectionError)

    def test_abstract_implementation_error(self) -> None:
        """Should reject abstract classes as implementations."""
        error = InvalidRegistrationError(
            MockService,
            "Cannot register abstract class AbstractService as implementation",
        )

        error_str = str(error)
        assert "abstract" in error_str
        assert "AbstractService" in error_str

    def test_none_implementation_error(self) -> None:
        """Should reject None as implementation."""
        error = InvalidRegistrationError(
            MockService, "Implementation type cannot be None"
        )

        assert "cannot be None" in str(error)


class TestDependencyInjectionError:
    """Test base exception class."""

    def test_base_exception_inheritance(self) -> None:
        """Should inherit from Exception."""
        error = DependencyInjectionError("Base error message")

        assert isinstance(error, Exception)
        assert str(error) == "Base error message"

    def test_all_exceptions_inherit_from_base(self) -> None:
        """All DI exceptions should inherit from base."""
        exceptions = [
            DependencyResolutionError(MockService, "test"),
            CircularDependencyError(["A", "B"]),
            DuplicateRegistrationError(MockService, "test"),
            InvalidRegistrationError(MockService, "test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, DependencyInjectionError)
            assert isinstance(exc, Exception)
