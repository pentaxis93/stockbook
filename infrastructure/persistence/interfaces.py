"""
Protocol interfaces for database connection abstraction.

Defines the contract that all database connection implementations must follow,
enabling clean architecture and dependency inversion.
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator, Protocol, runtime_checkable


@runtime_checkable
class IDatabaseConnection(Protocol):
    """
    Protocol interface for database connection implementations.

    This protocol defines the contract that both DatabaseConnection and
    TransactionalDatabaseConnection must implement, allowing repositories
    to work with either connection type through the same interface.

    This follows the Dependency Inversion Principle - repositories depend
    on this abstraction rather than concrete implementations.
    """

    def get_connection(self) -> sqlite3.Connection:
        """
        Get the underlying SQLite connection.

        Returns:
            Active SQLite connection instance
        """
        # Protocol method - implementation required by concrete classes

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Get a transaction context manager.

        For regular connections, this creates a new transaction.
        For transactional connections, this yields the existing transaction connection.

        Yields:
            SQLite connection within transaction context
        """
        yield  # type: ignore

    def initialize_schema(self) -> None:
        """
        Initialize database schema with required tables and indexes.

        This method should be idempotent - safe to call multiple times.
        """
        # Protocol method - implementation required by concrete classes
