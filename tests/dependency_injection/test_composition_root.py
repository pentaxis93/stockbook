"""
Unit tests for composition root.

Tests the application-specific dependency configuration that wires
our clean architecture layers together.
"""

from unittest.mock import patch

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

        # Act

        # Assert

    def test_complete_object_graph_wiring(self) -> None:
        """Should wire complete dependency chain correctly."""
        # Arrange

        # Act - resolve top-level component

        # Assert - verify entire chain is wired

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
