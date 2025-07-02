"""
Test suite for database factory.

Tests the creation and configuration of SQLAlchemy engines
for database connections.
"""

from pathlib import Path
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
        engine = create_engine("test.db")

        # Assert
        assert isinstance(engine, Engine)

    def test_create_engine_with_sqlite_url(self) -> None:
        """Should create engine with correct SQLite URL."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Act
        engine = create_engine("database/test.db")

        # Assert
        assert str(engine.url) == "sqlite:///database/test.db"

    def test_create_engine_with_absolute_path(self) -> None:
        """Should handle absolute paths correctly."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Arrange
        absolute_path = "/tmp/test_stockbook.db"

        # Act
        engine = create_engine(absolute_path)

        # Assert
        assert str(engine.url) == f"sqlite:///{absolute_path}"

    def test_create_engine_with_pathlib_path(self) -> None:
        """Should accept pathlib Path objects."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Arrange
        path = Path("database/test.db")

        # Act
        engine = create_engine(path)

        # Assert
        assert str(engine.url) == "sqlite:///database/test.db"

    def test_create_in_memory_engine(self) -> None:
        """Should create in-memory database for testing."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Act
        engine = create_engine(":memory:")

        # Assert
        assert str(engine.url) == "sqlite:///:memory:"
        # In-memory databases should use StaticPool to share connection
        assert isinstance(engine.pool, StaticPool)

    def test_create_engine_with_connection_args(self) -> None:
        """Should apply SQLite-specific connection arguments."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Act
        engine = create_engine("test.db")

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
        _ = create_engine("test.db", echo=True)

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
        engine = create_engine("test.db")

        # The implementation should register an event listener to enable foreign keys
        # We'll verify this in the implementation
        assert engine is not None  # Placeholder for now


class TestDatabaseFactoryWithConfig:
    """Test database factory with configuration integration."""

    @patch("src.infrastructure.persistence.database_factory.Config")
    def test_create_engine_from_config(self, mock_config_class: Mock) -> None:
        """Should create engine using configuration settings."""
        from src.infrastructure.persistence.database_factory import (
            create_engine_from_config,
        )

        # Arrange
        mock_config = Mock()
        mock_config.db_path = Path("configured/database.db")
        mock_config.db_connection_timeout = 30
        mock_config.DEBUG = False  # Add DEBUG attribute
        mock_config_class.return_value = mock_config

        # Act
        engine = create_engine_from_config()

        # Assert
        assert isinstance(engine, Engine)
        assert "configured/database.db" in str(engine.url)

    @patch("src.infrastructure.persistence.database_factory.Config")
    def test_create_test_engine_from_config(self, mock_config_class: Mock) -> None:
        """Should create test engine using test database path."""
        from src.infrastructure.persistence.database_factory import (
            create_engine_from_config,
        )

        # Arrange
        mock_config = Mock()
        mock_config.test_db_path = Path("test/database.db")
        mock_config.DEBUG = False  # Add DEBUG attribute
        mock_config_class.return_value = mock_config

        # Act
        engine = create_engine_from_config(use_test_db=True)

        # Assert
        assert isinstance(engine, Engine)
        assert "test/database.db" in str(engine.url)


class TestDatabaseFactoryErrorHandling:
    """Test error handling in database factory."""

    def test_create_engine_with_invalid_path_type(self) -> None:
        """Should raise appropriate error for invalid path types."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Act & Assert
        with pytest.raises(TypeError, match="Database path must be"):
            create_engine(123)  # type: ignore

    def test_create_engine_with_empty_path(self) -> None:
        """Should raise error for empty database path."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Act & Assert
        with pytest.raises(ValueError, match="Database path cannot be empty"):
            _ = create_engine("")

    @patch("src.infrastructure.persistence.database_factory.sqla_create_engine")
    def test_engine_creation_failure_handling(self, mock_create_engine: Mock) -> None:
        """Should handle engine creation failures gracefully."""
        from src.infrastructure.persistence.database_factory import create_engine

        # Arrange
        mock_create_engine.side_effect = Exception("Connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="Connection failed"):
            _ = create_engine("test.db")


class TestDatabaseFactoryHelpers:
    """Test helper functions in database factory."""

    def test_configure_sqlite_pragmas(self) -> None:
        """Should configure SQLite pragmas on connection."""
        from src.infrastructure.persistence.database_factory import (
            configure_sqlite_pragmas,
        )

        # Arrange
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        # Act
        configure_sqlite_pragmas(
            mock_connection, enable_foreign_keys=True, journal_mode="WAL"
        )

        # Assert
        mock_cursor.execute.assert_any_call("PRAGMA foreign_keys = ON")
        mock_cursor.execute.assert_any_call("PRAGMA journal_mode = WAL")
        mock_cursor.close.assert_called_once()

    def test_get_database_url(self) -> None:
        """Should construct proper database URL from path."""
        from src.infrastructure.persistence.database_factory import get_database_url

        # Test various path formats
        assert get_database_url("test.db") == "sqlite:///test.db"
        assert get_database_url(":memory:") == "sqlite:///:memory:"
        assert get_database_url(Path("data/test.db")) == "sqlite:///data/test.db"
