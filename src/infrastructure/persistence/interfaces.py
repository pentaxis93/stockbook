"""
Database connection interfaces for infrastructure layer.

This module defines protocols for database connections to support
both regular and transactional connections while maintaining
clean architecture boundaries.
"""

# pyright: reportUnknownParameterType=false

from typing import Any, Dict, List, Optional, Protocol, Union


class IDatabaseConnection(Protocol):
    """
    Protocol for database connections supporting SQLAlchemy Core operations.

    This interface abstracts database connections to support both
    regular connections and transactional connections, allowing
    repositories to work with either type transparently.
    """

    def execute(
        self,
        statement: Any,  # SQLAlchemy ClauseElement
        parameters: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        execution_options: Optional[Dict[str, Any]] = None,
    ) -> Any:  # SQLAlchemy Result
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

    def commit(self) -> None:
        """
        Commit the current transaction.

        Note: This may be a no-op for connections already in a transaction
        managed by a Unit of Work.
        """

    def rollback(self) -> None:
        """
        Rollback the current transaction.

        Note: This may be a no-op for connections already in a transaction
        managed by a Unit of Work.
        """

    def close(self) -> None:
        """
        Close the connection.

        Note: This may be a no-op for connections managed by a connection pool
        or Unit of Work.
        """
