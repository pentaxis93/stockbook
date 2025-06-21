"""
Dependency injection container implementation.

Provides a clean interface for dependency registration and resolution
using dependency-injector library internally for robust functionality.
"""

import inspect
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from dependency_injector import containers, providers
from dependency_injector.errors import Error as DIError

from .exceptions import (
    CircularDependencyError,
    DependencyResolutionError,
    DuplicateRegistrationError,
    InvalidRegistrationError,
)
from .lifetimes import Lifetime

T = TypeVar("T")


class RegistrationInfo:
    """Information about a registered service."""

    def __init__(
        self, service_type: Type, implementation_type: Type, lifetime: Lifetime
    ):
        self.service_type = service_type
        self.implementation_type = implementation_type
        self.lifetime = lifetime


class DIContainer:
    """
    Dependency injection container that wraps dependency-injector
    to provide a clean, testable interface.
    """

    def __init__(self):
        """Initialize the DI container."""
        self._container = containers.DeclarativeContainer()
        self._registrations: Dict[Type, RegistrationInfo] = {}
        self._resolution_chain: List[str] = []

    def register_singleton(
        self, service_type: Type[T], implementation_type: Optional[Type[T]] = None
    ) -> None:
        """
        Register a type as singleton (single instance shared).

        Args:
            service_type: The service interface or class to register
            implementation_type: The concrete implementation (defaults to service_type)

        Raises:
            DuplicateRegistrationError: If service_type is already registered
            InvalidRegistrationError: If types are incompatible
        """
        implementation_type = implementation_type or service_type

        if self.is_registered(service_type):
            raise DuplicateRegistrationError(
                service_type, f"Service {service_type.__name__} is already registered"
            )

        self._validate_registration(service_type, implementation_type)

        try:
            # Create singleton provider with auto-wiring
            provider = providers.Singleton(implementation_type)
            provider.add_args(*self._get_constructor_args(implementation_type))
            setattr(self._container, self._get_provider_name(service_type), provider)

            # Track registration
            self._registrations[service_type] = RegistrationInfo(
                service_type, implementation_type, Lifetime.SINGLETON
            )

        except Exception as e:
            raise InvalidRegistrationError(
                service_type,
                f"Failed to register singleton {service_type.__name__}: {str(e)}",
            ) from e

    def register_transient(
        self, service_type: Type[T], implementation_type: Optional[Type[T]] = None
    ) -> None:
        """
        Register a type as transient (new instance each time).

        Args:
            service_type: The service interface or class to register
            implementation_type: The concrete implementation (defaults to service_type)

        Raises:
            DuplicateRegistrationError: If service_type is already registered
            InvalidRegistrationError: If types are incompatible
        """
        implementation_type = implementation_type or service_type

        if self.is_registered(service_type):
            raise DuplicateRegistrationError(
                service_type, f"Service {service_type.__name__} is already registered"
            )

        self._validate_registration(service_type, implementation_type)

        try:
            # Create factory provider for transient behavior with auto-wiring
            provider = providers.Factory(implementation_type)
            provider.add_args(*self._get_constructor_args(implementation_type))
            setattr(self._container, self._get_provider_name(service_type), provider)

            # Track registration
            self._registrations[service_type] = RegistrationInfo(
                service_type, implementation_type, Lifetime.TRANSIENT
            )

        except Exception as e:
            raise InvalidRegistrationError(
                service_type,
                f"Failed to register transient {service_type.__name__}: {str(e)}",
            ) from e

    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """
        Register a pre-created instance.

        Args:
            service_type: The service interface or class to register
            instance: The pre-created instance to register

        Raises:
            DuplicateRegistrationError: If service_type is already registered
            InvalidRegistrationError: If instance is not compatible with service_type
        """
        if self.is_registered(service_type):
            raise DuplicateRegistrationError(
                service_type, f"Service {service_type.__name__} is already registered"
            )

        if not isinstance(instance, service_type):
            raise InvalidRegistrationError(
                service_type,
                f"Instance of type {type(instance).__name__} is not compatible with service type {service_type.__name__}",
            )

        try:
            # Create object provider for pre-created instance
            provider = providers.Object(instance)
            setattr(self._container, self._get_provider_name(service_type), provider)

            # Track registration
            self._registrations[service_type] = RegistrationInfo(
                service_type, type(instance), Lifetime.SINGLETON
            )

        except Exception as e:
            raise InvalidRegistrationError(
                service_type,
                f"Failed to register instance for {service_type.__name__}: {str(e)}",
            ) from e

    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a factory function to create instances.

        Args:
            service_type: The service interface or class to register
            factory: Factory function that creates instances

        Raises:
            DuplicateRegistrationError: If service_type is already registered
            InvalidRegistrationError: If factory is invalid
        """
        if self.is_registered(service_type):
            raise DuplicateRegistrationError(
                service_type, f"Service {service_type.__name__} is already registered"
            )

        if not callable(factory):
            raise InvalidRegistrationError(
                service_type, f"Factory for {service_type.__name__} is not callable"
            )

        try:
            # Create callable provider for factory function
            provider = providers.Callable(factory)
            setattr(self._container, self._get_provider_name(service_type), provider)

            # Track registration (assume transient behavior for factories)
            self._registrations[service_type] = RegistrationInfo(
                service_type, service_type, Lifetime.TRANSIENT
            )

        except Exception as e:
            raise InvalidRegistrationError(
                service_type,
                f"Failed to register factory for {service_type.__name__}: {str(e)}",
            ) from e

    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve an instance of the specified type.

        Args:
            service_type: The type to resolve

        Returns:
            An instance of the requested type

        Raises:
            DependencyResolutionError: If the type cannot be resolved
            CircularDependencyError: If circular dependencies are detected
        """
        # Check for circular dependencies
        type_name = service_type.__name__
        if type_name in self._resolution_chain:
            # Find the circular part
            start_index = self._resolution_chain.index(type_name)
            circular_chain = self._resolution_chain[start_index:] + [type_name]
            raise CircularDependencyError(circular_chain)

        # Add to resolution chain
        self._resolution_chain.append(type_name)

        try:
            if not self.is_registered(service_type):
                raise DependencyResolutionError(
                    service_type,
                    f"Service {service_type.__name__} is not registered",
                    self._resolution_chain.copy(),
                )

            # Get the provider and resolve
            provider_name = self._get_provider_name(service_type)
            provider = getattr(self._container, provider_name)

            try:
                instance = provider()
                return instance
            except DIError as e:
                raise DependencyResolutionError(
                    service_type,
                    f"Failed to resolve {service_type.__name__}: {str(e)}",
                    self._resolution_chain.copy(),
                ) from e

        finally:
            # Remove from resolution chain
            if type_name in self._resolution_chain:
                self._resolution_chain.remove(type_name)

    def is_registered(self, service_type: Type) -> bool:
        """
        Check if a service type is registered.

        Args:
            service_type: The type to check

        Returns:
            True if registered, False otherwise
        """
        return service_type in self._registrations

    def get_registrations(self) -> List[Type]:
        """
        Get list of all registered service types.

        Returns:
            List of registered service types
        """
        return list(self._registrations.keys())

    def get_registration_info(self, service_type: Type) -> Optional[RegistrationInfo]:
        """
        Get registration information for a service type.

        Args:
            service_type: The type to get info for

        Returns:
            RegistrationInfo if registered, None otherwise
        """
        return self._registrations.get(service_type)

    def _validate_registration(
        self, service_type: Type, implementation_type: Type
    ) -> None:
        """Validate that implementation_type can be used for service_type."""
        if not inspect.isclass(implementation_type):
            raise InvalidRegistrationError(
                service_type,
                f"Implementation type {implementation_type} is not a class",
            )

        # Check if implementation is compatible with service type
        # For abstract base classes, check if implementation is a subclass
        if (
            hasattr(service_type, "__abstractmethods__")
            and service_type.__abstractmethods__
        ):
            if not issubclass(implementation_type, service_type):
                raise InvalidRegistrationError(
                    service_type,
                    f"Implementation {implementation_type.__name__} does not implement interface {service_type.__name__}",
                )

    def _get_provider_name(self, service_type: Type) -> str:
        """Generate a unique provider name for the service type."""
        return f"provider_{service_type.__name__}_{id(service_type)}"

    def _get_constructor_args(self, implementation_type: Type) -> List[Any]:
        """Get the constructor arguments for auto-wiring."""
        sig = inspect.signature(implementation_type.__init__)
        args = []

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                # Skip parameters without type annotations
                continue

            # Handle forward references (string type annotations)
            if isinstance(param_type, str):
                # For string type annotations, we need to look them up by name
                # in the registered types at resolution time
                def create_string_resolver(type_name):
                    def resolver():
                        # Find the registered type that matches this name
                        for registered_type in self._registrations.keys():
                            if registered_type.__name__ == type_name:
                                return self.resolve(registered_type)
                        raise DependencyResolutionError(
                            type(None),
                            f"No registered type found for forward reference '{type_name}'",
                            self._resolution_chain.copy(),
                        )

                    return resolver

                dependency_provider = providers.Callable(
                    create_string_resolver(param_type)
                )
            else:
                # Normal type annotation
                dependency_provider = providers.Callable(
                    lambda dep_type=param_type: self.resolve(dep_type)
                )

            args.append(dependency_provider)

        return args
