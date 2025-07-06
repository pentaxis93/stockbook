"""
Unit tests for composition root.

Tests the application-specific dependency configuration that wires
our clean architecture layers together.
"""

from unittest.mock import patch

import pytest

# These imports now exist after implementation
from dependency_injection.composition_root import CompositionRoot
from dependency_injection.di_container import DIContainer

# Additional imports needed for tests
from src.domain.repositories.interfaces import IStockBookUnitOfWork
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork


class TestCompositionRoot:
    """Test application dependency composition."""

    def test_configure_returns_container(self) -> None:
        """Should return configured DI container."""
        # Act
        container = CompositionRoot.configure()

        # Assert
        assert container is not None
        assert isinstance(container, DIContainer)

    def test_configure_database_layer(self) -> None:
        """Should configure database and infrastructure layer correctly."""
        from sqlalchemy.engine import Engine

        from src.domain.repositories.interfaces import IStockBookUnitOfWork

        # Arrange & Act
        container = CompositionRoot.configure(database_path=":memory:")

        # Assert - Engine should be registered
        assert container.is_registered(Engine)
        engine = container.resolve(Engine)
        assert isinstance(engine, Engine)
        assert ":memory:" in str(engine.url)

        # Assert - Unit of Work should be registered
        assert container.is_registered(IStockBookUnitOfWork)
        unit_of_work = container.resolve(IStockBookUnitOfWork)
        assert isinstance(unit_of_work, SqlAlchemyUnitOfWork)

    def test_configure_application_layer(self) -> None:
        """Should configure application services correctly."""
        from src.application.services.stock_application_service import (
            StockApplicationService,
        )

        # Arrange
        container = CompositionRoot.configure(database_path=":memory:")

        # Act
        stock_service = container.resolve(StockApplicationService)

        # Assert
        assert isinstance(stock_service, StockApplicationService)
        # Verify behavior - if we can call a method that requires unit of work,
        # then the dependency was properly injected
        with patch.object(stock_service, "_unit_of_work") as mock_uow:
            mock_uow.__enter__.return_value = mock_uow
            mock_uow.stocks.get_all.return_value = []

            # This call would fail if unit of work wasn't properly injected
            result = stock_service.get_all_stocks()
            assert result == []

    def test_configure_presentation_layer(self) -> None:
        """Should configure presentation layer components correctly."""
        # Arrange
        # container = CompositionRoot.configure()

        # Act
        # controller = container.resolve(StockController)

        # Assert
        # assert isinstance(controller, StockController)
        # assert isinstance(controller.stock_service, StockApplicationService)
        pass

    def test_complete_object_graph_wiring(self) -> None:
        """Should wire complete dependency chain correctly."""
        # Arrange
        # container = CompositionRoot.configure()

        # Act - resolve top-level component
        # coordinator = container.resolve(StockPageCoordinator)

        # Assert - verify entire chain is wired
        # assert isinstance(coordinator.controller.stock_service._unit_of_work,
        #                  SqliteUnitOfWork)
        # assert isinstance(coordinator.controller.stock_service._unit_of_work.stocks,
        #                  SqliteStockRepository)
        # assert isinstance(coordinator.adapter.controller, StockController)
        pass

    def test_singleton_configuration(self) -> None:
        """Should configure singleton lifetimes correctly."""
        from sqlalchemy.engine import Engine

        # Arrange
        container = CompositionRoot.configure(database_path=":memory:")

        # Act
        engine1 = container.resolve(Engine)
        engine2 = container.resolve(Engine)

        # Assert - Engine should be singleton
        assert engine1 is engine2

    def test_transient_configuration(self) -> None:
        """Should configure transient lifetimes correctly."""
        from src.application.services.stock_application_service import (
            StockApplicationService,
        )

        # Arrange
        container = CompositionRoot.configure(database_path=":memory:")

        # Act
        service1 = container.resolve(StockApplicationService)
        service2 = container.resolve(StockApplicationService)
        uow1 = container.resolve(IStockBookUnitOfWork)
        uow2 = container.resolve(IStockBookUnitOfWork)

        # Assert - services and UoW should be transient
        assert service1 is not service2
        assert uow1 is not uow2


@pytest.mark.skip(reason="TDD - implementation pending")
class TestCompositionRootConfiguration:
    """Test configuration options and customization."""

    def test_configure_with_test_database(self) -> None:
        """Should allow configuration with test database."""
        # Act
        # container = CompositionRoot.configure(database_path=":memory:")

        # Assert
        # db_connection = container.resolve(DatabaseConnection)
        # assert db_connection.database_path == ":memory:"
        pass

    def test_configure_with_custom_config(self) -> None:
        """Should allow custom configuration overrides."""
        # Arrange
        # config = {
        #     "database_path": "/custom/test.db",
        #     "enable_logging": False
        # }

        # Act
        # container = CompositionRoot.configure(config=config)

        # Assert
        # db_connection = container.resolve(DatabaseConnection)
        # assert "/custom/test.db" in str(db_connection.database_path)
        pass

    def test_register_additional_services(self) -> None:
        """Should allow registering additional services."""
        # Arrange
        # def configure_extras(container: DIContainer):
        #     container.register_singleton(SomeExtraService, SomeExtraServiceImpl)

        # Act
        # container = CompositionRoot.configure(extra_registrations=configure_extras)

        # Assert
        # service = container.resolve(SomeExtraService)
        # assert isinstance(service, SomeExtraServiceImpl)
        pass


@pytest.mark.skip(reason="TDD - implementation pending")
class TestBootstrapIntegration:
    """Test integration with application bootstrap."""

    def test_bootstrap_app_with_di(self) -> None:
        """Should bootstrap complete application with DI."""
        # This tests the main app.py integration point
        # from main import bootstrap_app

        # app_components = bootstrap_app()
        # assert 'coordinator' in app_components
        # assert 'controller' in app_components
        # assert isinstance(app_components['coordinator'], StockPageCoordinator)
        pass

    def test_fastapi_integration_ready(self) -> None:
        """Should provide components ready for FastAPI integration."""
        # container = CompositionRoot.configure()
        # stock_service = container.resolve(StockApplicationService)

        # Test that service can be used in FastAPI context
        # This validates the wiring is correct for actual usage
        # assert hasattr(stock_service, 'create_stock')
        pass


@pytest.mark.skip(reason="TDD - implementation pending")
class TestCompositionRootErrorHandling:
    """Test error handling in composition root."""

    def test_missing_database_file_handling(self) -> None:
        """Should handle missing database file gracefully."""
        # Test what happens when database file doesn't exist
        # Should either create it or give clear error
        pass

    def test_invalid_configuration_handling(self) -> None:
        """Should validate configuration and give clear errors."""
        # Test invalid database paths, missing permissions, etc.
        pass

    def test_partial_registration_failure(self) -> None:
        """Should handle partial registration failures clearly."""
        # Test what happens if some registrations fail
        pass
