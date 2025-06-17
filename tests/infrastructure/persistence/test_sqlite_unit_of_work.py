"""
Tests for SQLite Unit of Work implementation.

Following TDD approach - these tests define the expected behavior
of transaction management and repository coordination.
"""

import os
import tempfile

import pytest

from domain.entities.stock_entity import StockEntity
from domain.repositories.interfaces import IStockRepository
from domain.value_objects.stock_symbol import StockSymbol
from infrastructure.persistence.database_connection import DatabaseConnection
from infrastructure.persistence.unit_of_work import SqliteUnitOfWork


class TestSqliteUnitOfWork:
    """Test suite for SqliteUnitOfWork."""

    def setup_method(self):
        """Set up test database."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

        # Initialize database connection
        self.db_connection = DatabaseConnection(self.temp_db.name)
        self.db_connection.initialize_schema()

    def teardown_method(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_unit_of_work_provides_repository_access(self):
        """Should provide access to repository instances."""
        # Act
        uow = SqliteUnitOfWork(self.db_connection)

        # Assert
        assert hasattr(uow, "stocks")
        assert isinstance(uow.stocks, IStockRepository)
        # Note: Other repositories will be tested when implemented
        # assert hasattr(uow, 'portfolios')
        # assert hasattr(uow, 'transactions')
        # assert hasattr(uow, 'targets')
        # assert hasattr(uow, 'balances')
        # assert hasattr(uow, 'journal')

    def test_unit_of_work_context_manager_success(self):
        """Should support context manager protocol for transactions."""
        # Arrange
        uow = SqliteUnitOfWork(self.db_connection)
        stock = StockEntity(symbol=StockSymbol("AAPL"), name="Apple Inc.")

        # Act
        with uow:
            stock_id = uow.stocks.create(stock)
            uow.commit()

        # Assert - verify data was committed
        with uow:
            retrieved_stock = uow.stocks.get_by_id(stock_id)
            assert retrieved_stock is not None
            assert str(retrieved_stock.symbol) == "AAPL"

    def test_unit_of_work_rollback_on_exception(self):
        """Should rollback transaction when exception occurs."""
        # Arrange
        uow = SqliteUnitOfWork(self.db_connection)
        stock = StockEntity(symbol=StockSymbol("MSFT"), name="Microsoft Corp.")

        # Act & Assert
        with pytest.raises(RuntimeError):
            with uow:
                stock_id = uow.stocks.create(stock)
                # Simulate an error before commit
                raise RuntimeError("Simulated error")

        # Verify data was not committed (rollback occurred)
        with uow:
            # Try to find the stock - it shouldn't exist
            retrieved_stock = uow.stocks.get_by_symbol(StockSymbol("MSFT"))
            assert retrieved_stock is None

    def test_unit_of_work_explicit_commit(self):
        """Should commit changes when explicitly called."""
        # Arrange
        uow = SqliteUnitOfWork(self.db_connection)
        stock = StockEntity(symbol=StockSymbol("GOOGL"), name="Alphabet Inc.")

        # Act
        with uow:
            stock_id = uow.stocks.create(stock)
            # Don't commit yet - data should not be visible

            # In a separate UoW, verify data is not yet committed
            with SqliteUnitOfWork(self.db_connection) as other_uow:
                temp_stock = other_uow.stocks.get_by_symbol(StockSymbol("GOOGL"))
                assert temp_stock is None  # Not committed yet

            # Now commit
            uow.commit()

        # Assert - verify data is now committed
        with uow:
            retrieved_stock = uow.stocks.get_by_id(stock_id)
            assert retrieved_stock is not None
            assert str(retrieved_stock.symbol) == "GOOGL"

    def test_unit_of_work_explicit_rollback(self):
        """Should rollback changes when explicitly called."""
        # Arrange
        uow = SqliteUnitOfWork(self.db_connection)
        stock = StockEntity(symbol=StockSymbol("TSLA"), name="Tesla Inc.")

        # Act
        with uow:
            stock_id = uow.stocks.create(stock)
            # Explicitly rollback
            uow.rollback()

        # Assert - verify data was not committed
        with uow:
            retrieved_stock = uow.stocks.get_by_symbol(StockSymbol("TSLA"))
            assert retrieved_stock is None

    def test_unit_of_work_multiple_operations_in_transaction(self):
        """Should handle multiple operations in single transaction."""
        # Arrange
        uow = SqliteUnitOfWork(self.db_connection)
        stocks = [
            StockEntity(symbol=StockSymbol("AAPL"), name="Apple Inc."),
            StockEntity(symbol=StockSymbol("MSFT"), name="Microsoft Corp."),
            StockEntity(symbol=StockSymbol("GOOGL"), name="Alphabet Inc."),
        ]

        # Act
        with uow:
            stock_ids = []
            for stock in stocks:
                stock_id = uow.stocks.create(stock)
                stock_ids.append(stock_id)

            # All should be created but not yet committed
            assert len(stock_ids) == 3

            uow.commit()

        # Assert - all stocks should be committed
        with uow:
            for stock_id in stock_ids:
                retrieved_stock = uow.stocks.get_by_id(stock_id)
                assert retrieved_stock is not None

    def test_unit_of_work_nested_context_managers_not_supported(self):
        """Should handle nested context managers appropriately."""
        # Arrange
        uow = SqliteUnitOfWork(self.db_connection)

        # Act & Assert
        with uow:
            stock1 = StockEntity(symbol=StockSymbol("AMZN"), name="Amazon")
            uow.stocks.create(stock1)

            # Nested context should work but share same transaction
            with uow:
                stock2 = StockEntity(symbol=StockSymbol("META"), name="Meta")
                uow.stocks.create(stock2)
                uow.commit()

            # Both stocks should be committed
            assert uow.stocks.exists_by_symbol(StockSymbol("AMZN"))
            assert uow.stocks.exists_by_symbol(StockSymbol("META"))

    def test_unit_of_work_isolation_between_instances(self):
        """Should provide isolation between different UoW instances."""
        # Arrange
        stock = StockEntity(symbol=StockSymbol("NVDA"), name="NVIDIA Corp.")

        # Act
        uow1 = SqliteUnitOfWork(self.db_connection)
        uow2 = SqliteUnitOfWork(self.db_connection)

        with uow1:
            stock_id = uow1.stocks.create(stock)
            # Don't commit in uow1

            # uow2 should not see the uncommitted data
            with uow2:
                retrieved_stock = uow2.stocks.get_by_symbol(StockSymbol("NVDA"))
                assert retrieved_stock is None

            # Now commit in uow1
            uow1.commit()

        # uow2 should now see the committed data
        with uow2:
            retrieved_stock = uow2.stocks.get_by_symbol(StockSymbol("NVDA"))
            assert retrieved_stock is not None

    def test_unit_of_work_repository_consistency(self):
        """Should maintain repository consistency within transaction."""
        # Arrange
        uow = SqliteUnitOfWork(self.db_connection)
        stock = StockEntity(symbol=StockSymbol("IBM"), name="IBM Corp.")

        # Act
        with uow:
            # Create stock
            stock_id = uow.stocks.create(stock)

            # Retrieve through same repository instance
            retrieved_stock = uow.stocks.get_by_id(stock_id)
            assert retrieved_stock is not None

            # Update through same repository instance
            retrieved_stock.update_grade("A")
            success = uow.stocks.update(stock_id, retrieved_stock)
            assert success is True

            # Verify update within same transaction
            updated_stock = uow.stocks.get_by_id(stock_id)
            assert updated_stock.grade == "A"

            uow.commit()

    def test_unit_of_work_error_handling(self):
        """Should handle database errors properly."""
        # Arrange - Create UoW with invalid database path
        invalid_db = DatabaseConnection("/invalid/path/database.db")
        uow = SqliteUnitOfWork(invalid_db)

        # Act & Assert
        with pytest.raises(Exception):  # Should raise database error
            with uow:
                stock = StockEntity(symbol=StockSymbol("ERR"), name="Error Inc.")
                uow.stocks.create(stock)
                uow.commit()

    def test_unit_of_work_commit_without_context_manager(self):
        """Should handle commit/rollback outside context manager."""
        # Arrange
        uow = SqliteUnitOfWork(self.db_connection)
        stock = StockEntity(symbol=StockSymbol("SOLO"), name="Solo Inc.")

        # Act
        stock_id = uow.stocks.create(stock)
        uow.commit()

        # Assert
        retrieved_stock = uow.stocks.get_by_id(stock_id)
        assert retrieved_stock is not None
        assert str(retrieved_stock.symbol) == "SOLO"

    def test_unit_of_work_double_commit_is_safe(self):
        """Should handle multiple commit calls safely."""
        # Arrange
        uow = SqliteUnitOfWork(self.db_connection)
        stock = StockEntity(symbol=StockSymbol("SAFE"), name="Safe Inc.")

        # Act
        with uow:
            stock_id = uow.stocks.create(stock)
            uow.commit()
            uow.commit()  # Second commit should be safe/no-op

        # Assert
        retrieved_stock = uow.stocks.get_by_id(stock_id)
        assert retrieved_stock is not None

    def test_unit_of_work_double_rollback_is_safe(self):
        """Should handle multiple rollback calls safely."""
        # Arrange
        uow = SqliteUnitOfWork(self.db_connection)
        stock = StockEntity(symbol=StockSymbol("ROLL"), name="Rollback Inc.")

        # Act
        with uow:
            uow.stocks.create(stock)
            uow.rollback()
            uow.rollback()  # Second rollback should be safe/no-op

        # Assert
        retrieved_stock = uow.stocks.get_by_symbol(StockSymbol("ROLL"))
        assert retrieved_stock is None
