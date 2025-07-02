"""
Database connection adapter for SQLAlchemy.

This module provides an adapter that implements the IDatabaseConnection
protocol by wrapping SQLAlchemy connection objects.
"""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportAttributeAccessIssue=false
# mypy: disable-error-code="no-untyped-call,attr-defined"

from typing import Any, Dict, List, Optional, Union

from sqlalchemy.engine import Connection


class SqlAlchemyConnection:
    """
    Adapter that wraps SQLAlchemy connection to implement IDatabaseConnection.

    This adapter allows repositories to work with SQLAlchemy connections
    through the domain-defined interface, maintaining clean architecture
    separation between infrastructure and domain layers.
    """

    def __init__(self, connection: Connection) -> None:
        """
        Initialize the adapter with a SQLAlchemy connection.

        Args:
            connection: SQLAlchemy connection object to wrap
        """
        self._connection = connection

    def execute(
        self,
        statement: Any,
        parameters: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        execution_options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Execute a SQLAlchemy Core statement.

        Args:
            statement: SQLAlchemy statement to execute
            parameters: Optional parameters for the statement
            execution_options: Optional execution options

        Returns:
            Result object from SQLAlchemy

        Raises:
            Exception: Database-specific exceptions on failure
        """
        return self._connection.execute(
            statement,
            parameters=parameters,
            execution_options=execution_options,
        )

    def commit(self) -> None:
        """
        Commit the current transaction.

        Note: This commits the transaction started with begin().
        """
        # Get the current transaction and commit it
        if hasattr(self._connection, "_transaction") and self._connection._transaction:
            self._connection._transaction.commit()
        # For newer SQLAlchemy versions, commit the connection itself
        elif hasattr(self._connection, "commit"):
            self._connection.commit()

    def rollback(self) -> None:
        """
        Rollback the current transaction.

        Note: This rolls back the transaction started with begin().
        """
        # Get the current transaction and rollback
        if hasattr(self._connection, "_transaction") and self._connection._transaction:
            self._connection._transaction.rollback()
        # For newer SQLAlchemy versions, rollback the connection itself
        elif hasattr(self._connection, "rollback"):
            self._connection.rollback()

    def close(self) -> None:
        """
        Close the connection.

        Note: This may be a no-op for connections managed by a connection pool
        or Unit of Work.
        """
        self._connection.close()
