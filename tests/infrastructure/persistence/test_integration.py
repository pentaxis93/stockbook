"""
Integration tests for Unit of Work with real database.

Tests the complete integration of Unit of Work, repositories,
and SQLAlchemy with an in-memory SQLite database.
"""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportCallIssue=false, reportArgumentType=false
# mypy: disable-error-code="no-untyped-call"

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine

from dependency_injection.composition_root import CompositionRoot
from src.application.commands.stock import CreateStockCommand, CreateStockInputs
from src.application.services.stock_application_service import StockApplicationService
from src.domain.entities.stock import Stock
from src.domain.repositories.interfaces import (
    IStockBookUnitOfWork,
    IStockRepository,
)
from src.domain.value_objects import CompanyName, Grade, StockSymbol
from src.infrastructure.persistence.tables.stock_table import metadata, stock_table
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork


@pytest.fixture
def test_engine() -> Generator[Engine, None, None]:
    """Create an in-memory test database engine."""
    engine = create_engine("sqlite:///:memory:")
    # Create all tables
    metadata.create_all(engine)
    yield engine
    # Cleanup
    engine.dispose()


@pytest.fixture
def unit_of_work(test_engine: Engine) -> IStockBookUnitOfWork:
    """Create a unit of work with test database."""
    return SqlAlchemyUnitOfWork(test_engine)


@pytest.fixture
def stock_service(unit_of_work: IStockBookUnitOfWork) -> StockApplicationService:
    """Create stock application service with unit of work."""
    return StockApplicationService(unit_of_work)


class TestUnitOfWorkIntegration:
    """Test Unit of Work integration with real database."""

    def test_basic_unit_of_work_commit(self, test_engine: Engine) -> None:
        """Should commit changes to database."""
        # Arrange
        uow = SqlAlchemyUnitOfWork(test_engine)

        # Act
        with uow:
            stock = (
                Stock.Builder()
                .with_symbol(StockSymbol("TEST"))
                .with_company_name(CompanyName("Test Company"))
                .with_grade(Grade("A"))
                .build()
            )
            stock_id = uow.stocks.create(stock)
            uow.commit()

        # Assert - Verify in database
        with test_engine.connect() as conn:
            result = conn.execute(select(stock_table.c))
            rows = result.fetchall()

        assert len(rows) == 1
        assert rows[0].symbol == "TEST"
        assert rows[0].id == stock_id

    def test_create_stock_commits_to_database(
        self, stock_service: StockApplicationService, test_engine: Engine
    ) -> None:
        """Should create stock and commit to database."""
        # Arrange
        inputs = CreateStockInputs(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Test stock",
        )
        command = CreateStockCommand(inputs)

        # Act
        try:
            stock_dto = stock_service.create_stock(command)
        except Exception:
            raise

        # Assert - Verify stock was returned
        assert stock_dto.symbol == "AAPL"
        assert stock_dto.name == "Apple Inc."

        # Verify in database using a new unit of work (new connection)
        new_uow = SqlAlchemyUnitOfWork(test_engine)
        with new_uow:
            retrieved = new_uow.stocks.get_by_symbol(StockSymbol("AAPL"))
            assert retrieved is not None
            assert retrieved.company_name is not None
            assert retrieved.company_name.value == "Apple Inc."

        # Also verify with direct database query
        with test_engine.connect() as conn:
            result = conn.execute(
                select(stock_table.c).where(stock_table.c.symbol == "AAPL")
            )
            row = result.fetchone()

        assert row is not None
        assert row.symbol == "AAPL"
        assert row.company_name == "Apple Inc."
        assert row.sector == "Technology"
        assert row.industry_group == "Software"
        assert row.grade == "A"
        assert row.notes == "Test stock"

    def test_rollback_on_error_leaves_database_unchanged(
        self, unit_of_work: IStockBookUnitOfWork, test_engine: Engine
    ) -> None:
        """Should rollback transaction on error."""
        # Arrange - Create a stock directly
        with unit_of_work:
            stock = (
                Stock.Builder()
                .with_symbol(StockSymbol("MSFT"))
                .with_company_name(CompanyName("Microsoft"))
                .with_grade(Grade("A"))
                .build()
            )
            _ = unit_of_work.stocks.create(stock)
            unit_of_work.commit()

        # Act - Try to create duplicate (should fail)
        with pytest.raises(  # noqa: PT012
            ValueError,
            match="Stock with symbol MSFT already exists",
        ):
            with unit_of_work:
                duplicate = (
                    Stock.Builder()
                    .with_symbol(StockSymbol("MSFT"))
                    .with_company_name(CompanyName("Microsoft Duplicate"))
                    .with_grade(Grade("B"))
                    .build()
                )
                _ = unit_of_work.stocks.create(duplicate)
                unit_of_work.commit()  # Should fail due to unique constraint

        # Assert - Original stock unchanged
        with test_engine.connect() as conn:
            result = conn.execute(
                select(stock_table.c).where(stock_table.c.symbol == "MSFT")
            )
            rows = result.fetchall()

        assert len(rows) == 1
        assert rows[0].company_name == "Microsoft"
        assert rows[0].grade == "A"

    def test_multiple_operations_in_single_transaction(
        self, unit_of_work: IStockBookUnitOfWork, test_engine: Engine
    ) -> None:
        """Should handle multiple operations in single transaction."""
        # Act
        with unit_of_work:
            # Create multiple stocks
            stock1 = (
                Stock.Builder()
                .with_symbol(StockSymbol("GOOG"))
                .with_company_name(CompanyName("Google"))
                .with_grade(Grade("A"))
                .build()
            )
            stock2 = (
                Stock.Builder()
                .with_symbol(StockSymbol("AMZN"))
                .with_company_name(CompanyName("Amazon"))
                .with_grade(Grade("B"))
                .build()
            )

            _ = unit_of_work.stocks.create(stock1)
            _ = unit_of_work.stocks.create(stock2)
            unit_of_work.commit()

        # Assert - Both stocks in database
        with test_engine.connect() as conn:
            result = conn.execute(select(stock_table.c))
            rows = result.fetchall()

        assert len(rows) == 2
        symbols = {row.symbol for row in rows}
        assert symbols == {"GOOG", "AMZN"}

    def test_repository_operations_share_connection(
        self, unit_of_work: IStockBookUnitOfWork
    ) -> None:
        """Should ensure repositories share same connection."""
        with unit_of_work:
            # Create stock
            stock = (
                Stock.Builder()
                .with_symbol(StockSymbol("IBM"))
                .with_company_name(CompanyName("IBM Corp"))
                .with_grade(Grade("B"))
                .build()
            )
            stock_id = unit_of_work.stocks.create(stock)

            # Read back in same transaction (before commit)
            retrieved = unit_of_work.stocks.get_by_id(stock_id)

            assert retrieved is not None
            assert retrieved.symbol.value == "IBM"

    def test_lazy_repository_loading(self, unit_of_work: IStockBookUnitOfWork) -> None:
        """Should lazy load repositories only when accessed."""
        uow = unit_of_work
        assert isinstance(uow, SqlAlchemyUnitOfWork)

        # Test lazy loading by accessing repositories inside context
        with uow:
            # Access stocks repository - should work without error
            stocks_repo = uow.stocks
            assert stocks_repo is not None
            assert isinstance(stocks_repo, IStockRepository)

            # Access portfolios repository - should work without error
            portfolios_repo = uow.portfolios
            assert portfolios_repo is not None
            # Note: This is a placeholder repository, not yet implementing
            # IPortfolioRepository

            # Verify same instances are returned on subsequent calls
            assert uow.stocks is stocks_repo
            assert uow.portfolios is portfolios_repo


class TestDependencyInjectionIntegration:
    """Test dependency injection integration with Unit of Work."""

    def test_complete_di_configuration(self) -> None:
        """Should wire up complete application with DI."""
        # Arrange
        container = CompositionRoot.configure(database_path=":memory:")

        # Act - Resolve application service
        service = container.resolve(StockApplicationService)

        # Assert
        assert isinstance(service, StockApplicationService)

        # Create tables before testing
        engine = container.resolve(Engine)
        metadata.create_all(engine)

        # Verify the service can use its unit of work by calling a method
        stocks = service.get_all_stocks()
        assert isinstance(stocks, list)

    def test_end_to_end_stock_creation_with_di(self) -> None:
        """Should create stock through DI-configured service."""
        # Arrange
        container = CompositionRoot.configure(database_path=":memory:")
        engine = container.resolve(Engine)
        metadata.create_all(engine)
        service = container.resolve(StockApplicationService)

        # Act
        inputs = CreateStockInputs(
            symbol="TSLA",
            name="Tesla Inc.",
            sector="Technology",
            industry_group="Software",
            grade="B",
            notes="EV manufacturer",
        )
        command = CreateStockCommand(inputs)
        stock_dto = service.create_stock(command)

        # Assert
        assert stock_dto.symbol == "TSLA"
        assert stock_dto.name == "Tesla Inc."

        # Verify in database
        with engine.connect() as conn:
            result = conn.execute(
                select(stock_table.c).where(stock_table.c.symbol == "TSLA")
            )
            row = result.fetchone()

        assert row is not None
        assert row.company_name == "Tesla Inc."


class TestTransactionIsolation:
    """Test transaction isolation with Unit of Work."""

    def test_concurrent_unit_of_work_instances(self, test_engine: Engine) -> None:
        """Should handle multiple UoW instances correctly."""
        # Note: SQLite in-memory with StaticPool shares connections,
        # so true transaction isolation isn't possible. This test
        # verifies basic functionality with multiple UoW instances.

        uow1 = SqlAlchemyUnitOfWork(test_engine)
        uow2 = SqlAlchemyUnitOfWork(test_engine)

        # Create and commit in uow1
        with uow1:
            stock = (
                Stock.Builder()
                .with_symbol(StockSymbol("NFLX"))
                .with_company_name(CompanyName("Netflix"))
                .with_grade(Grade("A"))
                .build()
            )
            _ = uow1.stocks.create(stock)
            uow1.commit()

        # Verify in uow2
        with uow2:
            retrieved = uow2.stocks.get_by_symbol(StockSymbol("NFLX"))
            assert retrieved is not None
            assert retrieved.company_name is not None
            assert retrieved.company_name.value == "Netflix"

    def test_error_in_nested_operation_rolls_back_all(
        self, unit_of_work: IStockBookUnitOfWork, test_engine: Engine
    ) -> None:
        """Should rollback all operations on error."""
        # Act & Assert
        with pytest.raises(ValueError, match="Simulated error"):  # noqa: PT012
            with unit_of_work:
                # Create first stock
                stock1 = (
                    Stock.Builder()
                    .with_symbol(StockSymbol("META"))
                    .with_company_name(CompanyName("Meta"))
                    .with_grade(Grade("B"))
                    .build()
                )
                _ = unit_of_work.stocks.create(stock1)

                # Simulate error
                raise ValueError("Simulated error")

        # Assert - Nothing should be committed
        with test_engine.connect() as conn:
            result = conn.execute(select(stock_table.c))
            rows = result.fetchall()

        assert len(rows) == 0
