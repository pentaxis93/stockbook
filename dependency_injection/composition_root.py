"""
Composition root for dependency injection configuration.

Configures the entire application's dependency graph in one central location,
following clean architecture principles.
"""

from typing import Optional, Dict, Any, Callable
from .di_container import DIContainer

# Infrastructure layer imports
from infrastructure.persistence.database_connection import DatabaseConnection
from infrastructure.persistence.unit_of_work import SqliteUnitOfWork
from infrastructure.repositories.sqlite_stock_repository import SqliteStockRepository

# Domain layer imports
from domain.repositories.interfaces import IUnitOfWork, IStockRepository

# Application layer imports
from application.services.stock_application_service import StockApplicationService

# Presentation layer imports
from presentation.controllers.stock_controller import StockController
from presentation.adapters.streamlit_stock_adapter import StreamlitStockAdapter
from presentation.coordinators.stock_page_coordinator import StockPageCoordinator


class CompositionRoot:
    """
    Central configuration point for dependency injection.
    
    Responsible for wiring up the entire application dependency graph
    in a way that respects clean architecture boundaries.
    """
    
    @classmethod
    def configure(
        cls,
        database_path: str = "stockbook.db",
        config: Optional[Dict[str, Any]] = None,
        extra_registrations: Optional[Callable[[DIContainer], None]] = None
    ) -> DIContainer:
        """
        Configure the complete application dependency graph.
        
        Args:
            database_path: Path to the SQLite database file
            config: Optional configuration overrides
            extra_registrations: Optional function to register additional services
            
        Returns:
            Configured DIContainer ready for use
        """
        container = DIContainer()
        config = config or {}
        
        # Override database path from config if provided
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
    def _configure_infrastructure_layer(cls, container: DIContainer, database_path: str) -> None:
        """Configure infrastructure layer dependencies."""
        
        # Database connection - singleton for connection pooling
        container.register_factory(
            DatabaseConnection,
            lambda: DatabaseConnection(database_path)
        )
        
        # Unit of Work - singleton to ensure transaction consistency
        container.register_singleton(IUnitOfWork, SqliteUnitOfWork)
        
        # Repositories - transient since they're lightweight
        container.register_transient(IStockRepository, SqliteStockRepository)
    
    @classmethod
    def _configure_application_layer(cls, container: DIContainer) -> None:
        """Configure application layer dependencies."""
        
        # Application services - transient to avoid state issues
        container.register_transient(StockApplicationService)
    
    @classmethod
    def _configure_presentation_layer(cls, container: DIContainer) -> None:
        """Configure presentation layer dependencies."""
        
        # Controllers - transient for request isolation
        container.register_transient(StockController)
        
        # Adapters - transient for UI state isolation  
        container.register_transient(StreamlitStockAdapter)
        
        # Coordinators - transient for page-level state management
        container.register_transient(StockPageCoordinator)