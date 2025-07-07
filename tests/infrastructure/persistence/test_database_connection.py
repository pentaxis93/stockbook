"""
Test suite for SqlAlchemyConnection adapter class.

Tests the database connection adapter that implements IDatabaseConnection
protocol to wrap SQLAlchemy connection objects.
"""

# pyright: reportPrivateUsage=false, reportCallIssue=false, reportUnusedCallResult=false

from unittest.mock import Mock

import pytest
from sqlalchemy.engine import Connection
from sqlalchemy.exc import DatabaseError

from src.infrastructure.persistence.database_connection import SqlAlchemyConnection
from src.infrastructure.persistence.interfaces import IDatabaseConnection


class TestSqlAlchemyConnectionConstruction:
    """Test SqlAlchemyConnection construction and initialization."""

    def test_accepts_sqlalchemy_connection(self) -> None:
        """Should accept SQLAlchemy connection in constructor."""
        # Arrange
        mock_connection = Mock(spec=Connection)

        # Act
        adapter = SqlAlchemyConnection(mock_connection)

        # Assert
        assert isinstance(adapter, IDatabaseConnection)
        # Verify adapter was created successfully - the fact that it's an instance
        # of SqlAlchemyConnection proves it accepted the connection

    def test_requires_connection_parameter(self) -> None:
        """Should require connection parameter in constructor."""
        # Act & Assert
        with pytest.raises(TypeError):
            SqlAlchemyConnection()  # pylint: disable=no-value-for-parameter


class TestSqlAlchemyConnectionExecute:
    """Test the execute method of SqlAlchemyConnection."""

    def test_execute_delegates_to_wrapped_connection(self) -> None:
        """Should delegate execute calls to wrapped SQLAlchemy connection."""
        # Arrange
        mock_connection = Mock(spec=Connection)
        mock_result = Mock()
        mock_connection.execute.return_value = mock_result

        adapter = SqlAlchemyConnection(mock_connection)

        mock_statement = Mock()  # SQLAlchemy statement
        parameters = {"param1": "value1"}
        execution_options = {"timeout": 30}

        # Act
        result = adapter.execute(
            mock_statement,
            parameters=parameters,
            execution_options=execution_options,
        )

        # Assert
        assert result is mock_result
        mock_connection.execute.assert_called_once_with(
            mock_statement,
            parameters=parameters,
            execution_options=execution_options,
        )

    def test_execute_with_no_optional_parameters(self) -> None:
        """Should handle execute with only statement parameter."""
        # Arrange
        mock_connection = Mock(spec=Connection)
        mock_result = Mock()
        mock_connection.execute.return_value = mock_result

        adapter = SqlAlchemyConnection(mock_connection)
        mock_statement = Mock()

        # Act
        result = adapter.execute(mock_statement)

        # Assert
        assert result is mock_result
        mock_connection.execute.assert_called_once_with(
            mock_statement,
            parameters=None,
            execution_options=None,
        )

    def test_execute_propagates_database_errors(self) -> None:
        """Should propagate database errors from wrapped connection."""
        # Arrange
        mock_connection = Mock(spec=Connection)
        mock_connection.execute.side_effect = DatabaseError(
            "Connection lost",
            params={},
            orig=Exception(),
        )

        adapter = SqlAlchemyConnection(mock_connection)
        mock_statement = Mock()

        # Act & Assert
        with pytest.raises(DatabaseError, match="Connection lost"):
            adapter.execute(mock_statement)


class TestSqlAlchemyConnectionCommit:
    """Test the commit method of SqlAlchemyConnection."""

    def test_commit_delegates_to_connection(self) -> None:
        """Should delegate commit to the connection if it has commit method."""
        # Arrange
        mock_connection = Mock(spec=Connection)
        mock_connection.commit = Mock()
        adapter = SqlAlchemyConnection(mock_connection)

        # Act
        adapter.commit()

        # Assert
        mock_connection.commit.assert_called_once()

    def test_commit_with_no_commit_method(self) -> None:
        """Should handle gracefully when connection has no commit method."""
        # Arrange
        mock_connection = Mock(spec=Connection)
        # Don't add commit method to mock
        delattr(mock_connection, "commit")
        adapter = SqlAlchemyConnection(mock_connection)

        # Act - should not raise
        adapter.commit()

        # Assert - nothing to assert, just checking it doesn't raise

    def test_commit_returns_none(self) -> None:
        """Should return None when called."""
        # Arrange
        mock_connection = Mock(spec=Connection)
        mock_connection.commit = Mock()
        adapter = SqlAlchemyConnection(mock_connection)

        # Act
        result = adapter.commit()  # pylint: disable=assignment-from-no-return

        # Assert
        assert result is None


class TestSqlAlchemyConnectionRollback:
    """Test the rollback method of SqlAlchemyConnection."""

    def test_rollback_delegates_to_connection(self) -> None:
        """Should delegate rollback to the connection if it has rollback method."""
        # Arrange
        mock_connection = Mock(spec=Connection)
        mock_connection.rollback = Mock()
        adapter = SqlAlchemyConnection(mock_connection)

        # Act
        adapter.rollback()

        # Assert
        mock_connection.rollback.assert_called_once()

    def test_rollback_returns_none(self) -> None:
        """Should return None when called."""
        # Arrange
        mock_connection = Mock(spec=Connection)
        adapter = SqlAlchemyConnection(mock_connection)

        # Act
        result = adapter.rollback()  # pylint: disable=assignment-from-no-return

        # Assert
        assert result is None


class TestSqlAlchemyConnectionClose:
    """Test the close method of SqlAlchemyConnection."""

    def test_close_delegates_to_wrapped_connection(self) -> None:
        """Should delegate close to wrapped connection."""
        # Arrange
        mock_connection = Mock(spec=Connection)
        adapter = SqlAlchemyConnection(mock_connection)

        # Act
        adapter.close()

        # Assert
        mock_connection.close.assert_called_once_with()

    def test_close_propagates_errors(self) -> None:
        """Should propagate close errors from wrapped connection."""
        # Arrange
        mock_connection = Mock(spec=Connection)
        mock_connection.close.side_effect = DatabaseError(
            "Cannot close",
            params={},
            orig=Exception(),
        )

        adapter = SqlAlchemyConnection(mock_connection)

        # Act & Assert
        with pytest.raises(DatabaseError, match="Cannot close"):
            adapter.close()

    def test_close_is_idempotent(self) -> None:
        """Should handle multiple close calls gracefully."""
        # Arrange
        mock_connection = Mock(spec=Connection)
        adapter = SqlAlchemyConnection(mock_connection)

        # Act
        adapter.close()
        adapter.close()  # Second call

        # Assert
        assert mock_connection.close.call_count == 2
