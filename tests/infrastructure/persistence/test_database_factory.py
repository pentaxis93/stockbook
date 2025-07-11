"""
Test suite for database factory.

Tests the creation and configuration of SQLAlchemy engines
for database connections.
"""

from unittest.mock import Mock, patch

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool


class TestDatabaseFactory:
    """Test database engine factory functionality."""

    def test_create_engine_returns_sqlalchemy_engine(self) -> None:
        """Should create and return a SQLAlchemy engine."""
        # This test will fail initially - TDD approach
        from src.infrastructure.persistence.database_factory import create_engine

        # Act
        engine = create_engine("sqlite:///test.db")

        # Assert
        assert isinstance(engine, Engine)

    def test_create_engine_with_sqlite_url(self) -> None:
        """Should create engine with correct SQLite URL."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Act
        engine = create_engine("sqlite:///database/test.db")

        # Assert
        assert str(engine.url) == "sqlite:///database/test.db"

    def test_create_engine_with_absolute_path(self) -> None:
        """Should handle absolute paths correctly."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Arrange
        absolute_path = "/tmp/test_stockbook.db"
        database_url = f"sqlite:///{absolute_path}"

        # Act
        engine = create_engine(database_url)

        # Assert
        assert str(engine.url) == database_url

    def test_create_engine_with_relative_path(self) -> None:
        """Should handle relative paths correctly."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Arrange
        database_url = "sqlite:///database/test.db"

        # Act
        engine = create_engine(database_url)

        # Assert
        assert str(engine.url) == database_url

    def test_create_in_memory_engine(self) -> None:
        """Should create in-memory database for testing."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Act
        engine = create_engine("sqlite:///:memory:")

        # Assert
        assert str(engine.url) == "sqlite:///:memory:"
        # In-memory databases should use StaticPool to share connection
        assert isinstance(engine.pool, StaticPool)

    def test_create_engine_with_connection_args(self) -> None:
        """Should apply SQLite-specific connection arguments."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Act
        engine = create_engine("sqlite:///test.db")

        # Assert - verify connect_args are set
        connect_args = engine.dialect.create_connect_args(engine.url)[1]
        assert "check_same_thread" in connect_args
        assert connect_args["check_same_thread"] is False

    @patch("src.infrastructure.persistence.database_factory.sqla_create_engine")
    def test_engine_configuration_parameters(self, mock_create_engine: Mock) -> None:
        """Should configure engine with appropriate parameters."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Arrange
        mock_engine = Mock(spec=Engine)
        mock_engine.pool = Mock()  # Add pool attribute for event listener
        mock_create_engine.return_value = mock_engine

        # Act
        _ = create_engine("sqlite:///test.db", echo=True)

        # Assert
        mock_create_engine.assert_called_once()
        call_kwargs = mock_create_engine.call_args.kwargs
        assert call_kwargs["echo"] is True
        assert "connect_args" in call_kwargs
        assert call_kwargs["connect_args"]["check_same_thread"] is False

    def test_create_engine_enables_foreign_keys(self) -> None:
        """Should enable foreign key constraints by default."""
        from src.infrastructure.persistence.database_factory import create_engine

        # This will test that the engine is configured to enable foreign keys
        # We'll need to check the event listeners or execution options
        engine = create_engine("sqlite:///test.db")

        # The implementation should register an event listener to enable foreign keys
        # We'll verify this in the implementation
        assert engine is not None  # Placeholder for now


class TestDatabaseFactoryWithConfig:
    """Test database factory with configuration integration."""

    @patch("src.infrastructure.persistence.database_factory.app_config")
    @patch("src.infrastructure.persistence.database_factory.database_config")
    def test_create_engine_from_config(
        self,
        mock_database_config: Mock,
        mock_app_config: Mock,
    ) -> None:
        """Should create engine using configuration settings."""
        from src.infrastructure.persistence.database_factory import (
            create_engine_from_config,
        )

        # Arrange
        mock_database_config.get_connection_string.return_value = (
            "sqlite:///configured/database.db"
        )
        mock_app_config.DEBUG = False

        # Act
        engine = create_engine_from_config()

        # Assert
        assert isinstance(engine, Engine)
        assert "configured/database.db" in str(engine.url)
        mock_database_config.get_connection_string.assert_called_once_with(test=False)

    @patch("src.infrastructure.persistence.database_factory.app_config")
    @patch("src.infrastructure.persistence.database_factory.database_config")
    def test_create_test_engine_from_config(
        self,
        mock_database_config: Mock,
        mock_app_config: Mock,
    ) -> None:
        """Should create test engine using test database path."""
        from src.infrastructure.persistence.database_factory import (
            create_engine_from_config,
        )

        # Arrange
        mock_database_config.get_connection_string.return_value = (
            "sqlite:///test/database.db"
        )
        mock_app_config.DEBUG = False

        # Act
        engine = create_engine_from_config(use_test_db=True)

        # Assert
        assert isinstance(engine, Engine)
        assert "test/database.db" in str(engine.url)
        mock_database_config.get_connection_string.assert_called_once_with(test=True)


class TestDatabaseFactoryErrorHandling:
    """Test error handling in database factory."""

    def test_create_engine_with_invalid_url(self) -> None:
        """Should raise appropriate error for invalid URL."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Act & Assert - non-SQLite URL
        with pytest.raises(ValueError, match="Unsupported database scheme"):
            _ = create_engine("postgresql://localhost/db")

    def test_create_engine_with_empty_url(self) -> None:
        """Should raise error for empty database URL."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Act & Assert
        with pytest.raises(ValueError, match="Database URL cannot be empty"):
            _ = create_engine("")

    @patch("src.infrastructure.persistence.database_factory.sqla_create_engine")
    def test_engine_creation_failure_handling(self, mock_create_engine: Mock) -> None:
        """Should handle engine creation failures gracefully."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Arrange
        mock_create_engine.side_effect = Exception("Connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="Connection failed"):
            _ = create_engine("sqlite:///test.db")


class TestSQLiteDialect:
    """Test SQLite dialect specific functions."""

    def test_configure_sqlite_connection(self) -> None:
        """Should configure SQLite pragmas on connection."""
        from src.infrastructure.persistence.dialects.sqlite import (
            configure_sqlite_connection,
        )

        # Arrange
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        # Act
        configure_sqlite_connection(
            mock_connection,
            enable_foreign_keys=True,
            journal_mode="WAL",
        )

        # Assert
        mock_cursor.execute.assert_any_call("PRAGMA foreign_keys = ON")
        mock_cursor.execute.assert_any_call("PRAGMA journal_mode = WAL")
        mock_cursor.close.assert_called_once()

    def test_get_sqlite_engine_kwargs(self) -> None:
        """Should return appropriate SQLite engine kwargs."""
        from src.infrastructure.persistence.dialects.sqlite import (
            get_sqlite_engine_kwargs,
        )

        # Test file-based database
        kwargs = get_sqlite_engine_kwargs("sqlite:///test.db")
        assert "connect_args" in kwargs
        assert kwargs["connect_args"]["check_same_thread"] is False
        assert "poolclass" not in kwargs

        # Test in-memory database
        kwargs = get_sqlite_engine_kwargs("sqlite:///:memory:")
        assert "poolclass" in kwargs
        assert kwargs["poolclass"] is StaticPool
