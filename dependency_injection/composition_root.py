"""
Composition root for dependency injection configuration.

Configures the entire application's dependency graph in one central location,
following clean architecture principles.
"""

from typing import Any, Callable, Dict, Optional

# Configuration
from config import Config

# Application layer imports
from src.application.services.stock_application_service import StockApplicationService

# Domain layer imports
from src.domain.repositories.interfaces import IStockBookUnitOfWork, IStockRepository

# Infrastructure layer imports
from src.infrastructure.persistence.database_connection import DatabaseConnection
from src.infrastructure.persistence.unit_of_work import SqliteUnitOfWork
from src.infrastructure.repositories.sqlite_stock_repository import (
    SqliteStockRepository,
)
from src.presentation.adapters.stock_presentation_adapter import (
    StockPresentationAdapter,
)

# Presentation layer imports
from src.presentation.controllers.stock_controller import StockController
from src.presentation.coordinators.stock_page_coordinator import StockPageCoordinator

from .di_container import DIContainer


class CompositionRoot:
    """
    Central configuration point for dependency injection.

    Responsible for wiring up the entire application dependency graph
    in a way that respects clean architecture boundaries.
    """

    @classmethod
    def configure(
        cls,
        database_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        extra_registrations: Optional[Callable[[DIContainer], None]] = None,
    ) -> DIContainer:
        """
        Configure the complete application dependency graph.

        Args:
            database_path: Path to the SQLite database file (defaults to Config.db_path)
            config: Optional configuration overrides
            extra_registrations: Optional function to register additional services

        Returns:
            Configured DIContainer ready for use
        """
        container = DIContainer()
        config = config or {}

        # Use Config class database path as default, then check overrides
        if database_path is None:
            database_path = str(Config().db_path)
        db_path = config.get("database_path", database_path)

        # Configure infrastructure layer (outermost layer)
        cls._configure_infrastructure_layer(container, db_path)

        # Configure application layer (business logic)
        cls._configure_application_layer(container)

        # Configure presentation layer (UI/controllers)
        cls._configure_presentation_layer(container)

        # Apply any additional registrations
        if extra_registrations:
            extra_registrations(container)

        return container

    @classmethod
    def _configure_infrastructure_layer(
        cls, container: DIContainer, database_path: str
    ) -> None:
        """Configure infrastructure layer dependencies."""

        # Database connection - singleton for connection pooling
        def create_database_connection() -> DatabaseConnection:
            connection = DatabaseConnection(database_path)
            connection.initialize_schema()  # Ensure schema exists
            return connection

        container.register_factory(DatabaseConnection, create_database_connection)

        # Unit of Work - singleton to ensure transaction consistency
        container.register_singleton(IStockBookUnitOfWork, SqliteUnitOfWork)

        # Repositories - transient since they're lightweight
        container.register_transient(IStockRepository, SqliteStockRepository)

    @classmethod
    def _configure_application_layer(cls, container: DIContainer) -> None:
        """Configure application layer dependencies."""

        # Application services - transient to avoid state issues
        container.register_transient(StockApplicationService, StockApplicationService)

    @classmethod
    def _configure_presentation_layer(cls, container: DIContainer) -> None:
        """Configure presentation layer dependencies."""

        # Controllers - transient for request isolation
        container.register_transient(StockController, StockController)

        # Framework-agnostic adapter - transient for UI state isolation
        container.register_transient(StockPresentationAdapter, StockPresentationAdapter)

        # Coordinators - transient for page-level state management
        container.register_transient(StockPageCoordinator, StockPageCoordinator)
