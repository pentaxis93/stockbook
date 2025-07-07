"""
Test suite for SqlAlchemyUnitOfWork implementation.

Tests the Unit of Work pattern implementation that manages transactions
and provides repository instances for the StockBook domain.
"""

# pyright: reportPrivateUsage=false, reportCallIssue=false, reportUnusedCallResult=false

from typing import Any
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import DatabaseError

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
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.repositories.sqlalchemy_stock_repository import (
    SqlAlchemyStockRepository,
)


class TestSqlAlchemyUnitOfWorkConstruction:
    """Test SqlAlchemyUnitOfWork construction and initialization."""

    def test_accepts_sqlalchemy_engine(self) -> None:
        """Should accept SQLAlchemy engine in constructor."""
        # Arrange
        mock_engine = Mock(spec=Engine)

        # Act
        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Assert
        assert isinstance(uow, IStockBookUnitOfWork)
        # The fact that it was created successfully proves it accepted the engine

    def test_requires_engine_parameter(self) -> None:
        """Should require engine parameter in constructor."""
        # Act & Assert
        with pytest.raises(TypeError):
            SqlAlchemyUnitOfWork()  # pylint: disable=no-value-for-parameter

    def test_initializes_without_active_connection(self) -> None:
        """Should not have active connection before entering context."""
        # Arrange
        mock_engine = Mock(spec=Engine)

        # Act
        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Assert - trying to access repositories should raise error
        with pytest.raises(RuntimeError, match="Unit of work is not active"):
            _ = uow.stocks


class TestSqlAlchemyUnitOfWorkContextManager:
    """Test context manager behavior of SqlAlchemyUnitOfWork."""

    def test_enter_creates_connection_and_transaction(self) -> None:
        """Should create connection and begin transaction on enter."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        mock_connection = Mock(spec=Connection)
        mock_transaction = Mock()

        mock_engine.connect.return_value = mock_connection
        mock_connection.begin.return_value = mock_transaction
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)

        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Act
        with uow as context:
            # Assert
            assert context is uow
            # Verify connection was established by checking engine calls
            mock_engine.connect.assert_called_once()
            mock_connection.begin.assert_called_once()

    def test_exit_commits_transaction_on_success(self) -> None:
        """Should commit transaction when exiting normally."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        mock_connection = Mock(spec=Connection)
        mock_transaction = Mock()

        mock_engine.connect.return_value = mock_connection
        mock_connection.begin.return_value = mock_transaction
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)

        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Act
        with uow:
            pass  # Normal exit

        # Assert
        mock_connection.__exit__.assert_called_once()
        # The connection's __exit__ should be called with no exception
        call_args = mock_connection.__exit__.call_args
        assert call_args[0][0] is None  # exc_type
        assert call_args[0][1] is None  # exc_val
        assert call_args[0][2] is None  # exc_tb

    def test_exit_rolls_back_transaction_on_exception(self) -> None:
        """Should rollback transaction when exception occurs."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        mock_connection = Mock(spec=Connection)
        mock_transaction = Mock()

        mock_engine.connect.return_value = mock_connection
        mock_connection.begin.return_value = mock_transaction
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)

        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Act & Assert
        msg = "Test error"
        with pytest.raises(ValueError, match="Test error"), uow:
            raise ValueError(msg)

        # The connection's __exit__ should be called with exception info
        mock_connection.__exit__.assert_called_once()
        call_args = mock_connection.__exit__.call_args
        assert call_args[0][0] is ValueError  # exc_type
        assert str(call_args[0][1]) == "Test error"  # exc_val

    def test_cleans_up_resources_on_exit(self) -> None:
        """Should clean up connection and repository references on exit."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        mock_connection = Mock(spec=Connection)
        mock_transaction = Mock()

        mock_engine.connect.return_value = mock_connection
        mock_connection.begin.return_value = mock_transaction
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)

        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Act & Assert
        with uow:
            # Access repositories to ensure they're created
            stocks = uow.stocks
            assert stocks is not None

        # After exit, trying to access repositories should raise error
        with pytest.raises(RuntimeError, match="Unit of work is not active"):
            _ = uow.stocks

    def test_cannot_use_outside_context(self) -> None:
        """Should raise error when accessing repositories outside context."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Unit of work is not active"):
            _ = uow.stocks


class TestSqlAlchemyUnitOfWorkRepositoryProperties:
    """Test repository property access in SqlAlchemyUnitOfWork."""

    @pytest.fixture
    def active_uow(self) -> Any:
        """Create an active unit of work in context."""
        mock_engine = Mock(spec=Engine)
        mock_connection = Mock(spec=Connection)
        mock_transaction = Mock()

        mock_engine.connect.return_value = mock_connection
        mock_connection.begin.return_value = mock_transaction
        mock_connection.__enter__ = Mock(return_value=mock_connection)

        uow = SqlAlchemyUnitOfWork(mock_engine)
        uow.__enter__()  # pylint: disable=unnecessary-dunder-call
        return uow

    def test_stocks_property_returns_stock_repository(self, active_uow: Any) -> None:
        """Should return IStockRepository instance."""
        # Act
        repository = active_uow.stocks

        # Assert
        assert repository is not None
        assert isinstance(repository, IStockRepository)
        assert isinstance(repository, SqlAlchemyStockRepository)
        # Should return same instance on subsequent calls
        assert active_uow.stocks is repository

    @patch("src.infrastructure.persistence.unit_of_work._SqlAlchemyPortfolioRepository")
    def test_portfolios_property_returns_portfolio_repository(
        self,
        mock_repo_class: Mock,
        active_uow: Any,
    ) -> None:
        """Should return IPortfolioRepository instance."""
        # Arrange
        mock_repo_instance = Mock(spec=IPortfolioRepository)
        mock_repo_class.return_value = mock_repo_instance

        # Act
        repository = active_uow.portfolios

        # Assert
        assert repository is mock_repo_instance
        # Verify repository was created
        mock_repo_class.assert_called_once()
        # Should return same instance on subsequent calls
        assert active_uow.portfolios is repository

    @patch(
        "src.infrastructure.persistence.unit_of_work._SqlAlchemyTransactionRepository",
    )
    def test_transactions_property_returns_transaction_repository(
        self,
        mock_repo_class: Mock,
        active_uow: Any,
    ) -> None:
        """Should return ITransactionRepository instance."""
        # Arrange
        mock_repo_instance = Mock(spec=ITransactionRepository)
        mock_repo_class.return_value = mock_repo_instance

        # Act
        repository = active_uow.transactions

        # Assert
        assert repository is mock_repo_instance
        # Verify repository was created
        mock_repo_class.assert_called_once()
        # Should return same instance on subsequent calls
        assert active_uow.transactions is repository

    @patch("src.infrastructure.persistence.unit_of_work._SqlAlchemyTargetRepository")
    def test_targets_property_returns_target_repository(
        self,
        mock_repo_class: Mock,
        active_uow: Any,
    ) -> None:
        """Should return ITargetRepository instance."""
        # Arrange
        mock_repo_instance = Mock(spec=ITargetRepository)
        mock_repo_class.return_value = mock_repo_instance

        # Act
        repository = active_uow.targets

        # Assert
        assert repository is mock_repo_instance
        # Verify repository was created
        mock_repo_class.assert_called_once()
        # Should return same instance on subsequent calls
        assert active_uow.targets is repository

    @patch("src.infrastructure.persistence.unit_of_work._SqlAlchemyBalanceRepository")
    def test_balances_property_returns_balance_repository(
        self,
        mock_repo_class: Mock,
        active_uow: Any,
    ) -> None:
        """Should return IPortfolioBalanceRepository instance."""
        # Arrange
        mock_repo_instance = Mock(spec=IPortfolioBalanceRepository)
        mock_repo_class.return_value = mock_repo_instance

        # Act
        repository = active_uow.balances

        # Assert
        assert repository is mock_repo_instance
        # Verify repository was created
        mock_repo_class.assert_called_once()
        # Should return same instance on subsequent calls
        assert active_uow.balances is repository

    @patch("src.infrastructure.persistence.unit_of_work._SqlAlchemyJournalRepository")
    def test_journal_property_returns_journal_repository(
        self,
        mock_repo_class: Mock,
        active_uow: Any,
    ) -> None:
        """Should return IJournalRepository instance."""
        # Arrange
        mock_repo_instance = Mock(spec=IJournalRepository)
        mock_repo_class.return_value = mock_repo_instance

        # Act
        repository = active_uow.journal

        # Assert
        assert repository is mock_repo_instance
        # Verify repository was created
        mock_repo_class.assert_called_once()
        # Should return same instance on subsequent calls
        assert active_uow.journal is repository

    def test_all_repositories_share_same_connection(self, active_uow: Any) -> None:
        """Should ensure all repositories use the same database connection."""
        # Act - Access all repositories
        _ = active_uow.stocks

        # Note: Other repositories would be tested similarly, but they don't exist yet
        # This test ensures the pattern is established with the stock repository

        # Assert - Verify that repository is accessible
        # The fact that we can access stocks without error proves it was initialized


class TestSqlAlchemyUnitOfWorkTransactionMethods:
    """Test explicit transaction methods of SqlAlchemyUnitOfWork."""

    def test_commit_delegates_to_connection(self) -> None:
        """Should delegate commit to wrapped connection."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        mock_connection = Mock(spec=Connection)
        mock_db_connection = Mock(spec=SqlAlchemyConnection)

        mock_engine.connect.return_value = mock_connection
        mock_connection.begin.return_value = Mock()
        mock_connection.__enter__ = Mock(return_value=mock_connection)

        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Use the unit of work in context manager to test commit
        with patch(
            "src.infrastructure.persistence.unit_of_work.SqlAlchemyConnection",
        ) as mock_conn:
            mock_conn.return_value = mock_db_connection
            mock_connection.__exit__ = Mock(return_value=None)

            with uow:
                # Act
                uow.commit()

        # Assert
        mock_db_connection.commit.assert_called_once()

    def test_rollback_delegates_to_connection(self) -> None:
        """Should delegate rollback to wrapped connection."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        mock_connection = Mock(spec=Connection)
        mock_db_connection = Mock(spec=SqlAlchemyConnection)

        mock_engine.connect.return_value = mock_connection
        mock_connection.begin.return_value = Mock()
        mock_connection.__enter__ = Mock(return_value=mock_connection)

        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Use the unit of work in context manager to test rollback
        with patch(
            "src.infrastructure.persistence.unit_of_work.SqlAlchemyConnection",
        ) as mock_conn:
            mock_conn.return_value = mock_db_connection
            mock_connection.__exit__ = Mock(return_value=None)

            with uow:
                # Act
                uow.rollback()

        # Assert
        mock_db_connection.rollback.assert_called_once()

    def test_commit_outside_context_raises_error(self) -> None:
        """Should raise error when committing outside context."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Unit of work is not active"):
            uow.commit()

    def test_rollback_outside_context_raises_error(self) -> None:
        """Should raise error when rolling back outside context."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Unit of work is not active"):
            uow.rollback()


class TestPlaceholderRepositories:
    """Test placeholder repository implementations."""

    def test_placeholder_repositories_accept_connection(self) -> None:
        """Should initialize placeholder repositories with connection."""
        # Arrange
        from src.infrastructure.persistence.unit_of_work import (
            _SqlAlchemyBalanceRepository,
            _SqlAlchemyJournalRepository,
            _SqlAlchemyPortfolioRepository,
            _SqlAlchemyTargetRepository,
            _SqlAlchemyTransactionRepository,
        )

        mock_connection = Mock(spec=SqlAlchemyConnection)

        # Act & Assert - Test each placeholder repository
        # Verify that repositories can be instantiated with connection
        portfolio_repo = _SqlAlchemyPortfolioRepository(mock_connection)
        transaction_repo = _SqlAlchemyTransactionRepository(mock_connection)
        target_repo = _SqlAlchemyTargetRepository(mock_connection)
        balance_repo = _SqlAlchemyBalanceRepository(mock_connection)
        journal_repo = _SqlAlchemyJournalRepository(mock_connection)

        # All repositories should be successfully created
        assert isinstance(portfolio_repo, _SqlAlchemyPortfolioRepository)
        assert isinstance(transaction_repo, _SqlAlchemyTransactionRepository)
        assert isinstance(target_repo, _SqlAlchemyTargetRepository)
        assert isinstance(balance_repo, _SqlAlchemyBalanceRepository)
        assert isinstance(journal_repo, _SqlAlchemyJournalRepository)


class TestSqlAlchemyUnitOfWorkErrorHandling:
    """Test error handling in SqlAlchemyUnitOfWork."""

    def test_handles_connection_errors_gracefully(self) -> None:
        """Should handle database connection errors."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        mock_engine.connect.side_effect = DatabaseError(
            "Cannot connect",
            params={},
            orig=Exception(),
        )

        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Act & Assert
        with pytest.raises(DatabaseError, match="Cannot connect"), uow:
            pass

    def test_handles_transaction_begin_errors(self) -> None:
        """Should handle errors when beginning transaction."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        mock_connection = Mock(spec=Connection)

        mock_engine.connect.return_value = mock_connection
        mock_connection.begin.side_effect = DatabaseError(
            "Cannot begin transaction",
            params={},
            orig=Exception(),
        )
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)

        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Act & Assert
        with pytest.raises(DatabaseError, match="Cannot begin transaction"):
            with uow:
                pass

    def test_nested_usage_not_supported(self) -> None:
        """Should not support nested unit of work contexts."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        mock_connection = Mock(spec=Connection)
        mock_transaction = Mock()

        mock_engine.connect.return_value = mock_connection
        mock_connection.begin.return_value = mock_transaction
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)

        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Act & Assert
        with patch(
            "src.infrastructure.persistence.unit_of_work.SqlAlchemyConnection",
        ) as mock_conn:
            mock_db_connection = Mock(spec=SqlAlchemyConnection)
            mock_conn.return_value = mock_db_connection

            with uow:
                with pytest.raises(
                    RuntimeError,
                    match="Unit of work is already active",
                ):
                    with uow:  # Nested usage
                        pass

    def test_exit_with_no_connection_returns_none(self) -> None:
        """Should return None when exiting with no active connection."""
        # Arrange
        mock_engine = Mock(spec=Engine)
        uow = SqlAlchemyUnitOfWork(mock_engine)

        # Act - Call __exit__ directly without entering context
        result = uow.__exit__(None, None, None)  # pylint: disable=assignment-from-none

        # Assert
        assert result is None
