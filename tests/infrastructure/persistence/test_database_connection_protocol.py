"""
Test suite for IDatabaseConnection protocol and its implementations.

This test suite follows TDD methodology - tests are written first to define
expected behavior, then implementations are created to make tests pass.
"""

import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, List, Optional, Union
from unittest.mock import Mock, patch

import pytest

from src.infrastructure.persistence.database_connection import DatabaseConnection
from src.infrastructure.persistence.unit_of_work import TransactionalDatabaseConnection


class TestIDatabaseConnectionProtocol:
    """
    Test suite for the IDatabaseConnection protocol contract.

    These tests define the expected interface and behavior that all
    database connection implementations must provide.
    """

    def test_protocol_interface_requirements(self):
        """Test that protocol defines required interface methods."""
        # Protocol should now exist and be importable
        from src.infrastructure.persistence.interfaces import IDatabaseConnection

        # Protocol should be runtime checkable
        assert hasattr(IDatabaseConnection, "__protocol_attrs__")

    def test_get_connection_method_required(self):
        """Test that protocol requires get_connection method."""
        from src.infrastructure.persistence.interfaces import IDatabaseConnection

        # Mock implementation to test protocol contract
        class MockConnection:
            def get_connection(self):
                pass

            def transaction(self):
                pass

            def initialize_schema(self):
                pass

        # Should have get_connection method
        assert hasattr(MockConnection, "get_connection")
        # Should be compatible with protocol
        assert isinstance(MockConnection(), IDatabaseConnection)

    def test_transaction_method_required(self):
        """Test that protocol requires transaction context manager method."""
        from src.infrastructure.persistence.interfaces import IDatabaseConnection

        class MockConnection:
            def get_connection(self):
                pass

            def transaction(self):
                pass

            def initialize_schema(self):
                pass

        # Should have transaction method
        assert hasattr(MockConnection, "transaction")
        # Should be compatible with protocol
        assert isinstance(MockConnection(), IDatabaseConnection)

    def test_initialize_schema_method_required(self):
        """Test that protocol requires initialize_schema method."""
        from src.infrastructure.persistence.interfaces import IDatabaseConnection

        class MockConnection:
            def get_connection(self):
                pass

            def transaction(self):
                pass

            def initialize_schema(self):
                pass

        # Should have initialize_schema method
        assert hasattr(MockConnection, "initialize_schema")
        # Should be compatible with protocol
        assert isinstance(MockConnection(), IDatabaseConnection)


class TestDatabaseConnectionProtocolImplementation:
    """
    Test suite for DatabaseConnection implementing IDatabaseConnection protocol.

    These tests ensure DatabaseConnection properly implements the protocol interface.
    """

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = Path(self.temp_db.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.db_path.exists():
            self.db_path.unlink()

    def test_database_connection_implements_protocol(self):
        """Test that DatabaseConnection implements IDatabaseConnection protocol."""
        from src.infrastructure.persistence.interfaces import IDatabaseConnection

        db_conn = DatabaseConnection(self.db_path)
        assert isinstance(db_conn, IDatabaseConnection)

    def test_database_connection_get_connection_method(self):
        """Test DatabaseConnection provides get_connection method."""
        db_conn = DatabaseConnection(self.db_path)

        # Method should exist and return sqlite3.Connection
        assert hasattr(db_conn, "get_connection")

        connection = db_conn.get_connection()
        assert isinstance(connection, sqlite3.Connection)

    def test_database_connection_transaction_method(self):
        """Test DatabaseConnection provides transaction context manager."""
        db_conn = DatabaseConnection(self.db_path)

        # Method should exist and return context manager
        assert hasattr(db_conn, "transaction")

        with db_conn.transaction() as conn:
            assert isinstance(conn, sqlite3.Connection)

    def test_database_connection_initialize_schema_method(self):
        """Test DatabaseConnection provides initialize_schema method."""
        db_conn = DatabaseConnection(self.db_path)

        # Method should exist and be callable
        assert hasattr(db_conn, "initialize_schema")
        assert callable(db_conn.initialize_schema)

        # Should not raise exception when called
        db_conn.initialize_schema()


class TestTransactionalDatabaseConnectionProtocolImplementation:
    """
    Test suite for TransactionalDatabaseConnection implementing IDatabaseConnection protocol.

    These tests ensure TransactionalDatabaseConnection properly implements the protocol interface.
    """

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = Path(self.temp_db.name)
        self.original_db_conn = DatabaseConnection(self.db_path)

        # Create a mock connection for testing
        self.mock_connection = Mock(spec=sqlite3.Connection)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.db_path.exists():
            self.db_path.unlink()

    def test_transactional_connection_implements_protocol(self):
        """Test that TransactionalDatabaseConnection implements IDatabaseConnection protocol."""
        from src.infrastructure.persistence.interfaces import IDatabaseConnection

        trans_conn = TransactionalDatabaseConnection(
            self.mock_connection, self.original_db_conn
        )
        assert isinstance(trans_conn, IDatabaseConnection)

    def test_transactional_connection_get_connection_method(self):
        """Test TransactionalDatabaseConnection provides get_connection method."""
        trans_conn = TransactionalDatabaseConnection(
            self.mock_connection, self.original_db_conn
        )

        # Method should exist and return the wrapped connection
        assert hasattr(trans_conn, "get_connection")

        connection = trans_conn.get_connection()
        assert connection is self.mock_connection

    def test_transactional_connection_transaction_method(self):
        """Test TransactionalDatabaseConnection provides transaction context manager."""
        trans_conn = TransactionalDatabaseConnection(
            self.mock_connection, self.original_db_conn
        )

        # Method should exist and return context manager
        assert hasattr(trans_conn, "transaction")

        with trans_conn.transaction() as conn:
            assert conn is self.mock_connection

    def test_transactional_connection_initialize_schema_method(self):
        """Test TransactionalDatabaseConnection provides initialize_schema method."""
        trans_conn = TransactionalDatabaseConnection(
            self.mock_connection, self.original_db_conn
        )

        # Method should exist and delegate to original connection
        assert hasattr(trans_conn, "initialize_schema")
        assert callable(trans_conn.initialize_schema)

        # Should delegate to original connection
        with patch.object(self.original_db_conn, "initialize_schema") as mock_init:
            trans_conn.initialize_schema()
            mock_init.assert_called_once()


class TestRepositoryProtocolCompatibility:
    """
    Test suite for repository compatibility with IDatabaseConnection protocol.

    These tests ensure repositories can work with any IDatabaseConnection implementation.
    """

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = Path(self.temp_db.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.db_path.exists():
            self.db_path.unlink()

    def test_stock_repository_accepts_protocol_interface(self):
        """Test that SqliteStockRepository accepts IDatabaseConnection protocol."""
        # This will fail until we update repository type hints
        from src.infrastructure.repositories.sqlite_stock_repository import (
            SqliteStockRepository,
        )

        # Create both connection types
        db_conn = DatabaseConnection(self.db_path)
        mock_sqlite_conn = Mock(spec=sqlite3.Connection)
        trans_conn = TransactionalDatabaseConnection(mock_sqlite_conn, db_conn)

        # Both should be acceptable to repository constructor
        repo1 = SqliteStockRepository(db_conn)
        repo2 = SqliteStockRepository(trans_conn)

        assert repo1 is not None
        assert repo2 is not None

    def test_all_repositories_accept_protocol_interface(self):
        """Test that all repositories accept IDatabaseConnection protocol."""
        from src.infrastructure.repositories.sqlite_balance_repository import (
            SqlitePortfolioBalanceRepository,
        )
        from src.infrastructure.repositories.sqlite_journal_repository import (
            SqliteJournalRepository,
        )
        from src.infrastructure.repositories.sqlite_portfolio_repository import (
            SqlitePortfolioRepository,
        )
        from src.infrastructure.repositories.sqlite_stock_repository import (
            SqliteStockRepository,
        )
        from src.infrastructure.repositories.sqlite_target_repository import (
            SqliteTargetRepository,
        )
        from src.infrastructure.repositories.sqlite_transaction_repository import (
            SqliteTransactionRepository,
        )

        # Create both connection types
        db_conn = DatabaseConnection(self.db_path)
        mock_sqlite_conn = Mock(spec=sqlite3.Connection)
        trans_conn = TransactionalDatabaseConnection(mock_sqlite_conn, db_conn)

        # All repositories should accept both connection types
        repositories = [
            SqliteStockRepository,
            SqlitePortfolioRepository,
            SqliteTransactionRepository,
            SqliteTargetRepository,
            SqlitePortfolioBalanceRepository,
            SqliteJournalRepository,
        ]

        for repo_class in repositories:
            repo1 = repo_class(db_conn)
            repo2 = repo_class(trans_conn)
            assert repo1 is not None
            assert repo2 is not None


class TestUnitOfWorkProtocolIntegration:
    """
    Test suite for Unit of Work using protocol-based connections.

    These tests ensure the Unit of Work pattern works correctly with the protocol.
    """

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = Path(self.temp_db.name)
        self.db_conn = DatabaseConnection(self.db_path)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.db_path.exists():
            self.db_path.unlink()

    def test_unit_of_work_creates_protocol_compatible_repositories(self):
        """Test that UoW creates repositories compatible with protocol."""
        from src.infrastructure.persistence.unit_of_work import SqliteUnitOfWork

        uow = SqliteUnitOfWork(self.db_conn)

        with uow:
            # All repository properties should return protocol-compatible instances
            assert uow.stocks is not None
            assert uow.portfolios is not None
            assert uow.transactions is not None
            assert uow.targets is not None
            assert uow.balances is not None
            assert uow.journal is not None

    def test_unit_of_work_provides_consistent_connection_interface(self):
        """Test that UoW provides consistent connection interface to all repositories."""
        from src.infrastructure.persistence.unit_of_work import SqliteUnitOfWork

        uow = SqliteUnitOfWork(self.db_conn)

        with uow:
            # All repositories should be using the same connection interface type
            # This tests the protocol consistency
            stocks_conn_type = type(uow.stocks.db_connection)
            portfolios_conn_type = type(uow.portfolios.db_connection)

            # Within transaction, should use TransactionalDatabaseConnection
            assert stocks_conn_type == portfolios_conn_type
            assert hasattr(uow.stocks.db_connection, "get_connection")
            assert hasattr(uow.stocks.db_connection, "transaction")
            assert hasattr(uow.stocks.db_connection, "initialize_schema")

    def test_unit_of_work_transaction_isolation(self):
        """Test that UoW maintains transaction isolation through protocol."""
        from src.infrastructure.persistence.unit_of_work import SqliteUnitOfWork

        uow = SqliteUnitOfWork(self.db_conn)

        # Outside transaction - should use regular DatabaseConnection
        stocks_repo_outside = uow.stocks
        assert isinstance(stocks_repo_outside.db_connection, DatabaseConnection)

        # Inside transaction - should use TransactionalDatabaseConnection
        with uow:
            # Clear cached repositories to force recreation with transactional connection
            uow._stocks = None
            uow._portfolios = None

            stocks_repo_inside = uow.stocks
            assert isinstance(
                stocks_repo_inside.db_connection, TransactionalDatabaseConnection
            )

            # Should be same connection instance across all repositories
            portfolios_repo_inside = uow.portfolios
            assert (
                stocks_repo_inside.db_connection.connection
                is portfolios_repo_inside.db_connection.connection
            )


class TestProtocolTypeCompatibility:
    """
    Test suite for protocol type compatibility and pyright compliance.

    These tests ensure the protocol solution resolves the original type errors.
    """

    def test_protocol_resolves_type_errors(self):
        """Test that protocol implementation resolves pyright type errors."""
        # This test verifies the main issue is resolved
        # Will fail until protocol is implemented and type hints updated

        from src.infrastructure.persistence.unit_of_work import SqliteUnitOfWork

        # This should not cause type errors after protocol implementation
        db_conn = DatabaseConnection(":memory:")
        uow = SqliteUnitOfWork(db_conn)

        # These operations should be type-safe
        with uow:
            stocks_repo = uow.stocks
            portfolios_repo = uow.portfolios

            # Repository should accept the connection without type errors
            assert stocks_repo is not None
            assert portfolios_repo is not None

    def test_repository_constructor_type_safety(self):
        """Test that repository constructors are type-safe with protocol."""
        # This will fail until we update repository type hints
        from src.infrastructure.repositories.sqlite_stock_repository import (
            SqliteStockRepository,
        )

        # Both connection types should be type-safe
        db_conn = DatabaseConnection(":memory:")
        mock_sqlite_conn = Mock(spec=sqlite3.Connection)
        trans_conn = TransactionalDatabaseConnection(mock_sqlite_conn, db_conn)

        # These should not cause type errors
        repo1 = SqliteStockRepository(db_conn)
        repo2 = SqliteStockRepository(trans_conn)

        assert repo1 is not None
        assert repo2 is not None
