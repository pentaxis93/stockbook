"""Composition root for dependency injection configuration.

Configures the entire application's dependency graph in one central location,
following clean architecture principles.
"""

from collections.abc import Callable
from typing import Any

from sqlalchemy.engine import Engine

# Application layer imports
from src.application.interfaces.stock_service import IStockApplicationService
from src.application.services.stock_application_service import StockApplicationService
from src.domain.repositories.interfaces import IStockBookUnitOfWork
from src.infrastructure.config import database_config
from src.infrastructure.persistence.database_factory import create_engine
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork

from .di_container import DIContainer

# Presentation layer imports removed - will be rebuilt later


# Domain layer imports
# Repository interfaces will be used when infrastructure is rebuilt

# Infrastructure layer imports removed - will be rebuilt later


class CompositionRoot:
    """Central configuration point for dependency injection.

    Responsible for wiring up the entire application dependency graph
    in a way that respects clean architecture boundaries.
    """

    @classmethod
    def configure(
        cls,
        database_url: str | None = None,
        config: dict[str, Any] | None = None,
        extra_registrations: Callable[[DIContainer], None] | None = None,
    ) -> DIContainer:
        """Configure the complete application dependency graph.

        Args:
            database_url: Database URL (defaults to Config.database_url)
            config: Optional configuration overrides
            extra_registrations: Optional function to register additional services

        Returns:
            Configured DIContainer ready for use
        """
        container = DIContainer()
        config = config or {}

        # Use database config URL as default, then check overrides
        if database_url is None:
            database_url = database_config.database_url
        db_url = config.get("database_url", database_url)

        # Configure infrastructure layer (database, repositories)
        cls._configure_infrastructure_layer(container, db_url)

        # Configure application layer (business logic)
        cls._configure_application_layer(container)

        # Presentation layer configuration removed - will be rebuilt later

        # Apply any additional registrations
        if extra_registrations:
            extra_registrations(container)

        return container

    @classmethod
    def _configure_infrastructure_layer(
        cls,
        container: DIContainer,
        db_url: str,
    ) -> None:
        """Configure infrastructure layer dependencies.

        Args:
            container: DI container to configure
            db_url: Database URL
        """
        # Database engine - singleton
        engine = create_engine(db_url)
        container.register_instance(Engine, engine)

        # Unit of Work - transient for transaction isolation
        container.register_factory(
            IStockBookUnitOfWork,
            lambda: SqlAlchemyUnitOfWork(container.resolve(Engine)),
        )

    @classmethod
    def _configure_application_layer(cls, container: DIContainer) -> None:
        """Configure application layer dependencies."""
        # Application services - transient to avoid state issues
        # Register the interface with its implementation
        container.register_factory(
            IStockApplicationService,
            lambda: StockApplicationService(container.resolve(IStockBookUnitOfWork)),
        )

    # Presentation layer configuration method removed - will be rebuilt later
