"""
SQLite implementation of the Unit of Work pattern.

Manages transaction boundaries and provides access to repositories
within a transactional context.
"""

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Generator, Optional, Type

from src.domain.repositories.interfaces import (
    IJournalRepository,
    IPortfolioBalanceRepository,
    IPortfolioRepository,
    IStockBookUnitOfWork,
    IStockRepository,
    ITargetRepository,
    ITransactionRepository,
)
from src.infrastructure.persistence.database_connection import DatabaseConnection
from src.infrastructure.persistence.interfaces import IDatabaseConnection
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


class TransactionalDatabaseConnection(IDatabaseConnection):
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

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Return a context manager that yields the same connection.

        Note: Since we're already in a transaction, this just yields
        the connection without creating a new transaction.
        """
        yield self.connection

    def initialize_schema(self) -> None:
        """Delegate schema initialization to original connection."""
        self.original_db_connection.initialize_schema()


@dataclass
class RepositoryContainer:
    """Container for repository instances in Unit of Work."""

    stocks: Optional[IStockRepository] = None
    portfolios: Optional[IPortfolioRepository] = None
    transactions: Optional[ITransactionRepository] = None
    targets: Optional[ITargetRepository] = None
    balances: Optional[IPortfolioBalanceRepository] = None
    journal: Optional[IJournalRepository] = None


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
        self._repositories = RepositoryContainer()
        self._nesting_level: int = 0

    @property
    def stocks(self) -> IStockRepository:
        """
        Get stock repository within current transaction context.

        Returns:
            Stock repository instance
        """
        if self._repositories.stocks is None:
            if self._connection is None:
                # Return a repository that can be accessed but will fail on operations
                self._repositories.stocks = SqliteStockRepository(self.db_connection)
            else:
                # Create a special connection wrapper for transactional context
                connection_wrapper = TransactionalDatabaseConnection(
                    self._connection, self.db_connection
                )
                self._repositories.stocks = SqliteStockRepository(connection_wrapper)
        return self._repositories.stocks

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

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
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
            # Outermost context - handle transaction and cleanup
            self._handle_transaction_completion(exc_type)
            self._cleanup_resources()

    def _handle_transaction_completion(
        self, exc_type: Optional[Type[BaseException]]
    ) -> None:
        """Handle transaction commit or rollback based on exception status."""
        if self._connection:
            try:
                if exc_type is None:
                    self._connection.commit()
                else:
                    self._connection.rollback()
            finally:
                self._connection.close()

    def _cleanup_resources(self) -> None:
        """Clean up all resources after transaction completion."""
        self._connection = None
        self._repositories = RepositoryContainer()

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
        if self._repositories.portfolios is None:
            if self._connection is None:
                self._repositories.portfolios = SqlitePortfolioRepository(
                    self.db_connection
                )
            else:
                connection_wrapper = TransactionalDatabaseConnection(
                    self._connection, self.db_connection
                )
                self._repositories.portfolios = SqlitePortfolioRepository(
                    connection_wrapper
                )
        return self._repositories.portfolios

    @property
    def transactions(self) -> ITransactionRepository:
        """Get transaction repository instance."""
        if self._repositories.transactions is None:
            if self._connection is None:
                self._repositories.transactions = SqliteTransactionRepository(
                    self.db_connection
                )
            else:
                connection_wrapper = TransactionalDatabaseConnection(
                    self._connection, self.db_connection
                )
                self._repositories.transactions = SqliteTransactionRepository(
                    connection_wrapper
                )
        return self._repositories.transactions

    @property
    def targets(self) -> ITargetRepository:
        """Get target repository instance."""
        if self._repositories.targets is None:
            if self._connection is None:
                self._repositories.targets = SqliteTargetRepository(self.db_connection)
            else:
                connection_wrapper = TransactionalDatabaseConnection(
                    self._connection, self.db_connection
                )
                self._repositories.targets = SqliteTargetRepository(connection_wrapper)
        return self._repositories.targets

    @property
    def balances(self) -> IPortfolioBalanceRepository:
        """Get portfolio balance repository instance."""
        if self._repositories.balances is None:
            if self._connection is None:
                self._repositories.balances = SqlitePortfolioBalanceRepository(
                    self.db_connection
                )
            else:
                connection_wrapper = TransactionalDatabaseConnection(
                    self._connection, self.db_connection
                )
                self._repositories.balances = SqlitePortfolioBalanceRepository(
                    connection_wrapper
                )
        return self._repositories.balances

    @property
    def journal(self) -> IJournalRepository:
        """Get journal repository instance."""
        if self._repositories.journal is None:
            if self._connection is None:
                self._repositories.journal = SqliteJournalRepository(self.db_connection)
            else:
                connection_wrapper = TransactionalDatabaseConnection(
                    self._connection, self.db_connection
                )
                self._repositories.journal = SqliteJournalRepository(connection_wrapper)
        return self._repositories.journal
