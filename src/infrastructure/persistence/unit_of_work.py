"""Unit of Work implementation using SQLAlchemy.

This module provides a concrete implementation of the Unit of Work pattern
using SQLAlchemy for transaction management and repository coordination.
"""

# pyright: reportUnknownMemberType=false

import types

from sqlalchemy.engine import Connection, Engine

from src.domain.repositories.interfaces import (
    IJournalRepository,
    IPortfolioBalanceRepository,
    IPortfolioRepository,
    IStockBookUnitOfWork,
    IStockRepository,
    ITargetRepository,
    ITransactionRepository,
)
from src.infrastructure.persistence.database_connection import SqlAlchemyConnection
from src.infrastructure.persistence.interfaces import IDatabaseConnection
from src.infrastructure.repositories.sqlalchemy_stock_repository import (
    SqlAlchemyStockRepository,
)


class SqlAlchemyUnitOfWork(IStockBookUnitOfWork):
    """SQLAlchemy implementation of the Unit of Work pattern.

    Manages database transactions and provides repository instances
    that share the same transactional connection.
    """

    def __init__(self, engine: Engine) -> None:
        """Initialize unit of work with SQLAlchemy engine.

        Args:
            engine: SQLAlchemy engine for database connections
        """
        self._engine = engine
        self._connection: Connection | None = None
        self._db_connection: IDatabaseConnection | None = None
        self._stocks: IStockRepository | None = None
        self._portfolios: IPortfolioRepository | None = None
        self._transactions: ITransactionRepository | None = None
        self._targets: ITargetRepository | None = None
        self._balances: IPortfolioBalanceRepository | None = None
        self._journal: IJournalRepository | None = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        """Enter the unit of work context.

        Creates a new database connection and begins a transaction.

        Returns:
            Self for use in context manager

        Raises:
            RuntimeError: If unit of work is already active (nested usage)
        """
        if self._connection is not None:
            msg = "Unit of work is already active"
            raise RuntimeError(msg)

        # Create connection and begin transaction
        self._connection = self._engine.connect()
        _ = self._connection.begin()

        # Wrap in our adapter
        self._db_connection = SqlAlchemyConnection(self._connection)

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> bool | None:
        """Exit the unit of work context.

        Commits transaction on success, rolls back on exception.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            None to propagate exceptions
        """
        if self._connection is None:
            return None

        try:
            # Let SQLAlchemy's connection context manager handle commit/rollback
            self._connection.__exit__(exc_type, exc_val, exc_tb)
        finally:
            # Clean up resources
            self._connection = None
            self._db_connection = None
            self._stocks = None
            self._portfolios = None
            self._transactions = None
            self._targets = None
            self._balances = None
            self._journal = None

        return None  # Propagate exceptions

    @property
    def stocks(self) -> IStockRepository:
        """Get stock repository instance."""
        self._ensure_active()
        if self._stocks is None:
            # _ensure_active guarantees _db_connection is not None
            # Use type guard to satisfy type checker and avoid assert
            if self._db_connection is None:  # pragma: no cover
                msg = "Database connection unexpectedly None"
                raise RuntimeError(msg)
            self._stocks = SqlAlchemyStockRepository(self._db_connection)
        return self._stocks

    @property
    def portfolios(self) -> IPortfolioRepository:
        """Get portfolio repository instance."""
        self._ensure_active()
        if self._portfolios is None:
            # _ensure_active guarantees _db_connection is not None
            # Use type guard to satisfy type checker and avoid assert
            if self._db_connection is None:  # pragma: no cover
                msg = "Database connection unexpectedly None"
                raise RuntimeError(msg)
            # TODO: Replace with actual implementation when available
            self._portfolios = _SqlAlchemyPortfolioRepository(self._db_connection)  # type: ignore[assignment]
        return self._portfolios  # type: ignore[return-value]

    @property
    def transactions(self) -> ITransactionRepository:
        """Get transaction repository instance."""
        self._ensure_active()
        if self._transactions is None:
            # _ensure_active guarantees _db_connection is not None
            # Use type guard to satisfy type checker and avoid assert
            if self._db_connection is None:  # pragma: no cover
                msg = "Database connection unexpectedly None"
                raise RuntimeError(msg)
            # TODO: Replace with actual implementation when available
            self._transactions = _SqlAlchemyTransactionRepository(self._db_connection)  # type: ignore[assignment]
        return self._transactions  # type: ignore[return-value]

    @property
    def targets(self) -> ITargetRepository:
        """Get target repository instance."""
        self._ensure_active()
        if self._targets is None:
            # _ensure_active guarantees _db_connection is not None
            # Use type guard to satisfy type checker and avoid assert
            if self._db_connection is None:  # pragma: no cover
                msg = "Database connection unexpectedly None"
                raise RuntimeError(msg)
            # TODO: Replace with actual implementation when available
            self._targets = _SqlAlchemyTargetRepository(self._db_connection)  # type: ignore[assignment]
        return self._targets  # type: ignore[return-value]

    @property
    def balances(self) -> IPortfolioBalanceRepository:
        """Get portfolio balance repository instance."""
        self._ensure_active()
        if self._balances is None:
            # _ensure_active guarantees _db_connection is not None
            # Use type guard to satisfy type checker and avoid assert
            if self._db_connection is None:  # pragma: no cover
                msg = "Database connection unexpectedly None"
                raise RuntimeError(msg)
            # TODO: Replace with actual implementation when available
            self._balances = _SqlAlchemyBalanceRepository(self._db_connection)  # type: ignore[assignment]
        return self._balances  # type: ignore[return-value]

    @property
    def journal(self) -> IJournalRepository:
        """Get journal repository instance."""
        self._ensure_active()
        if self._journal is None:
            # _ensure_active guarantees _db_connection is not None
            # Use type guard to satisfy type checker and avoid assert
            if self._db_connection is None:  # pragma: no cover
                msg = "Database connection unexpectedly None"
                raise RuntimeError(msg)
            # TODO: Replace with actual implementation when available
            self._journal = _SqlAlchemyJournalRepository(self._db_connection)  # type: ignore[assignment]
        return self._journal  # type: ignore[return-value]

    def commit(self) -> None:
        """Commit all changes made during this unit of work.

        Raises:
            RuntimeError: If unit of work is not active
            Exception: If commit fails for any reason
        """
        self._ensure_active()
        if self._db_connection is not None:
            self._db_connection.commit()

    def rollback(self) -> None:
        """Rollback all changes made during this unit of work.

        This should restore the system to the state it was in
        before this unit of work began.

        Raises:
            RuntimeError: If unit of work is not active
        """
        self._ensure_active()
        if self._db_connection is not None:
            self._db_connection.rollback()

    def _ensure_active(self) -> None:
        """Ensure unit of work is active.

        Raises:
            RuntimeError: If unit of work is not active
        """
        if self._connection is None or self._db_connection is None:
            msg = "Unit of work is not active"
            raise RuntimeError(msg)


# Placeholder repository classes - will be replaced with actual implementations
# These are only here to make the unit tests pass for now
# Using underscore prefix to indicate these are internal/temporary
class _SqlAlchemyPortfolioRepository:  # pylint: disable=too-few-public-methods
    """Placeholder for portfolio repository."""

    def __init__(self, connection: IDatabaseConnection) -> None:
        """Initialize placeholder repository with database connection."""
        self._connection = connection


class _SqlAlchemyTransactionRepository:  # pylint: disable=too-few-public-methods
    """Placeholder for transaction repository."""

    def __init__(self, connection: IDatabaseConnection) -> None:
        """Initialize placeholder repository with database connection."""
        self._connection = connection


class _SqlAlchemyTargetRepository:  # pylint: disable=too-few-public-methods
    """Placeholder for target repository."""

    def __init__(self, connection: IDatabaseConnection) -> None:
        """Initialize placeholder repository with database connection."""
        self._connection = connection


class _SqlAlchemyBalanceRepository:  # pylint: disable=too-few-public-methods
    """Placeholder for balance repository."""

    def __init__(self, connection: IDatabaseConnection) -> None:
        """Initialize placeholder repository with database connection."""
        self._connection = connection


class _SqlAlchemyJournalRepository:  # pylint: disable=too-few-public-methods
    """Placeholder for journal repository."""

    def __init__(self, connection: IDatabaseConnection) -> None:
        """Initialize placeholder repository with database connection."""
        self._connection = connection
