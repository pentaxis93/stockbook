"""
SQLite implementation of the Unit of Work pattern.

Manages transaction boundaries and provides access to repositories
within a transactional context.
"""

import sqlite3
from typing import Optional

from domain.repositories.interfaces import (IJournalRepository,
                                            IPortfolioBalanceRepository,
                                            IPortfolioRepository,
                                            IStockRepository,
                                            ITargetRepository,
                                            ITransactionRepository,
                                            IStockBookUnitOfWork)
from infrastructure.persistence.database_connection import DatabaseConnection
from infrastructure.repositories.sqlite_stock_repository import SqliteStockRepository
from infrastructure.repositories.sqlite_portfolio_repository import SqlitePortfolioRepository
from infrastructure.repositories.sqlite_transaction_repository import SqliteTransactionRepository
from infrastructure.repositories.sqlite_target_repository import SqliteTargetRepository
from infrastructure.repositories.sqlite_balance_repository import SqlitePortfolioBalanceRepository
from infrastructure.repositories.sqlite_journal_repository import SqliteJournalRepository


class TransactionalDatabaseConnection:
    """
    Database connection wrapper that provides the same connection
    for all operations within a Unit of Work transaction.
    """

    def __init__(
        self, connection: sqlite3.Connection, original_db_connection: DatabaseConnection
    ):
        """
        Initialize with an existing connection.

        Args:
            connection: Active SQLite connection
            original_db_connection: Original database connection for schema operations
        """
        self.connection = connection
        self.original_db_connection = original_db_connection
        self.is_transactional = True  # Flag to indicate this is transactional

    def get_connection(self) -> sqlite3.Connection:
        """Return the shared transaction connection."""
        return self.connection

    def transaction(self):
        """
        Return a context manager that yields the same connection.

        Note: Since we're already in a transaction, this just yields
        the connection without creating a new transaction.
        """
        return _TransactionContext(self.connection)

    def initialize_schema(self) -> None:
        """Delegate schema initialization to original connection."""
        self.original_db_connection.initialize_schema()


class _TransactionContext:
    """Helper context manager for the transactional connection."""

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def __enter__(self) -> sqlite3.Connection:
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Don't commit, rollback, or close here - that's managed by the Unit of Work
        pass


class SqliteUnitOfWork(IStockBookUnitOfWork):
    """
    SQLite-based implementation of the Unit of Work pattern.

    Manages transaction lifecycle and provides access to repositories
    within a consistent transactional context.
    """

    def __init__(self, db_connection: DatabaseConnection):
        """
        Initialize Unit of Work with database connection.

        Args:
            db_connection: Database connection manager
        """
        self.db_connection = db_connection
        self._connection: Optional[sqlite3.Connection] = None
        self._stocks: Optional[IStockRepository] = None
        self._portfolios: Optional[IPortfolioRepository] = None
        self._transactions: Optional[ITransactionRepository] = None
        self._targets: Optional[ITargetRepository] = None
        self._balances: Optional[IPortfolioBalanceRepository] = None
        self._journal: Optional[IJournalRepository] = None
        self._nesting_level: int = 0

    @property
    def stocks(self) -> IStockRepository:
        """
        Get stock repository within current transaction context.

        Returns:
            Stock repository instance
        """
        if self._stocks is None:
            if self._connection is None:
                # Return a repository that can be accessed but will fail on operations
                self._stocks = SqliteStockRepository(self.db_connection)
            else:
                # Create a special connection wrapper for transactional context
                connection_wrapper = TransactionalDatabaseConnection(
                    self._connection, self.db_connection
                )
                self._stocks = SqliteStockRepository(connection_wrapper)
        return self._stocks

    def __enter__(self) -> "SqliteUnitOfWork":
        """
        Enter transaction context.

        Supports nested context managers by sharing the same connection.

        Returns:
            Self for context manager protocol
        """
        self._nesting_level += 1
        if self._nesting_level == 1:
            # First enter - create the connection
            self._connection = self.db_connection.get_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit transaction context.

        Commits transaction on success, rolls back on exception.
        Only closes connection when exiting the outermost context.

        Args:
            exc_type: Exception type if any
            exc_val: Exception value if any
            exc_tb: Exception traceback if any
        """
        self._nesting_level -= 1

        if self._nesting_level == 0:
            # Outermost context - handle transaction
            if self._connection:
                try:
                    if exc_type is None:
                        self._connection.commit()
                    else:
                        self._connection.rollback()
                finally:
                    self._connection.close()
                    self._connection = None
                    self._stocks = None
                    self._portfolios = None
                    self._transactions = None
                    self._targets = None
                    self._balances = None
                    self._journal = None

    def commit(self) -> None:
        """
        Commit the current transaction.

        Note: If no transaction context is active, this is a no-op
        since operations have their own transaction management.
        """
        if self._connection is not None:
            self._connection.commit()

    def rollback(self) -> None:
        """
        Roll back the current transaction.

        Note: If no transaction context is active, this is a no-op
        since operations have their own transaction management.
        """
        if self._connection is not None:
            self._connection.rollback()

    @property
    def portfolios(self) -> IPortfolioRepository:
        """Get portfolio repository instance."""
        if self._portfolios is None:
            if self._connection is None:
                self._portfolios = SqlitePortfolioRepository(self.db_connection)
            else:
                connection_wrapper = TransactionalDatabaseConnection(
                    self._connection, self.db_connection
                )
                self._portfolios = SqlitePortfolioRepository(connection_wrapper)
        return self._portfolios

    @property
    def transactions(self) -> ITransactionRepository:
        """Get transaction repository instance."""
        if self._transactions is None:
            if self._connection is None:
                self._transactions = SqliteTransactionRepository(self.db_connection)
            else:
                connection_wrapper = TransactionalDatabaseConnection(
                    self._connection, self.db_connection
                )
                self._transactions = SqliteTransactionRepository(connection_wrapper)
        return self._transactions

    @property
    def targets(self) -> ITargetRepository:
        """Get target repository instance."""
        if self._targets is None:
            if self._connection is None:
                self._targets = SqliteTargetRepository(self.db_connection)
            else:
                connection_wrapper = TransactionalDatabaseConnection(
                    self._connection, self.db_connection
                )
                self._targets = SqliteTargetRepository(connection_wrapper)
        return self._targets

    @property
    def balances(self) -> IPortfolioBalanceRepository:
        """Get balance repository instance."""
        if self._balances is None:
            if self._connection is None:
                self._balances = SqlitePortfolioBalanceRepository(self.db_connection)
            else:
                connection_wrapper = TransactionalDatabaseConnection(
                    self._connection, self.db_connection
                )
                self._balances = SqlitePortfolioBalanceRepository(connection_wrapper)
        return self._balances

    @property
    def journal(self) -> IJournalRepository:
        """Get journal repository instance."""
        if self._journal is None:
            if self._connection is None:
                self._journal = SqliteJournalRepository(self.db_connection)
            else:
                connection_wrapper = TransactionalDatabaseConnection(
                    self._connection, self.db_connection
                )
                self._journal = SqliteJournalRepository(connection_wrapper)
        return self._journal
