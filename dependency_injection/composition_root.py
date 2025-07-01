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
from src.presentation.adapters.stock_presentation_adapter import (
    StockPresentationAdapter,
)

# Presentation layer imports
from src.presentation.controllers.stock_controller import StockController
from src.presentation.coordinators.stock_page_coordinator import StockPageCoordinator

from .di_container import DIContainer

# Domain layer imports
# Repository interfaces will be used when infrastructure is rebuilt

# Infrastructure layer imports removed - will be rebuilt later


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

        # Infrastructure layer configuration removed - will be rebuilt later
        # db_path parameter kept for future use
        _ = db_path  # Will be used when infrastructure is rebuilt

        # Configure application layer (business logic)
        cls._configure_application_layer(container)

        # Configure presentation layer (UI/controllers)
        cls._configure_presentation_layer(container)

        # Apply any additional registrations
        if extra_registrations:
            extra_registrations(container)

        return container

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
