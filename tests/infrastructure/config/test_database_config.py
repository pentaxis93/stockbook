"""Tests for infrastructure database configuration."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.infrastructure.config import DatabaseConfig, database_config


class TestDatabaseConfigSingleton:
    """Test database configuration singleton behavior."""

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        DatabaseConfig.reset()

    def test_database_config_singleton(self) -> None:
        """Test that DatabaseConfig implements singleton pattern."""
        config1 = DatabaseConfig()
        config2 = DatabaseConfig()
        assert config1 is config2

    def test_database_config_global_instance(self) -> None:
        """Test that global instance uses singleton pattern."""
        assert isinstance(database_config, DatabaseConfig)
        new_config = DatabaseConfig()
        assert new_config is DatabaseConfig()

    def test_reset_creates_new_instance(self) -> None:
        """Test that reset allows creating new instance."""
        config1 = DatabaseConfig()
        DatabaseConfig.reset()
        config2 = DatabaseConfig()
        assert config1 is not config2

    def test_multiple_init_calls_safe(self) -> None:
        """Test that multiple __init__ calls don't reinitialize."""
        config = DatabaseConfig()
        original_url = config.database_url

        # Manually call __init__ again
        config.__init__()

        # Should still have same values
        assert config.database_url == original_url


class TestDatabaseConfigDefaults:
    """Test default database configuration values."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        DatabaseConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        DatabaseConfig.reset()

    def test_default_database_urls(self) -> None:
        """Test default database URLs."""
        config = DatabaseConfig()
        assert config.database_url == "sqlite:///data/database/stockbook.db"
        assert config.test_database_url == "sqlite:///:memory:"

    def test_default_connection_settings(self) -> None:
        """Test default connection settings."""
        config = DatabaseConfig()
        assert config.connection_timeout == 30
        assert config.foreign_keys_enabled is True
        assert config.row_factory == "dict"

    def test_get_connection_string_default(self) -> None:
        """Test connection string retrieval for main database."""
        config = DatabaseConfig()
        assert config.get_connection_string() == config.database_url

    def test_get_connection_string_test(self) -> None:
        """Test connection string retrieval for test database."""
        config = DatabaseConfig()
        assert config.get_connection_string(test=True) == config.test_database_url

    def test_db_path_property(self) -> None:
        """Test db_path property returns Path object."""
        config = DatabaseConfig()
        assert config.db_path == Path("data/database/stockbook.db")

    def test_test_db_path_property(self) -> None:
        """Test test_db_path property for in-memory database."""
        config = DatabaseConfig()
        assert config.test_db_path == Path(":memory:")


class TestDatabaseConfigEnvironment:
    """Test environment variable handling."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        DatabaseConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        DatabaseConfig.reset()

    @patch.dict(os.environ, {"DATABASE_URL": "sqlite:///custom/path/database.db"})
    def test_database_url_from_env(self) -> None:
        """Test loading database URL from environment."""
        config = DatabaseConfig()
        assert config.database_url == "sqlite:///custom/path/database.db"

    @patch.dict(os.environ, {"TEST_DATABASE_URL": "sqlite:///test/custom.db"})
    def test_test_database_url_from_env(self) -> None:
        """Test loading test database URL from environment."""
        config = DatabaseConfig()
        assert config.test_database_url == "sqlite:///test/custom.db"

    @patch.dict(os.environ, {"STOCKBOOK_DB_TIMEOUT": "60"})
    def test_connection_timeout_from_env(self) -> None:
        """Test loading connection timeout from environment."""
        config = DatabaseConfig()
        assert config.connection_timeout == 60

    @patch.dict(os.environ, {"STOCKBOOK_DB_FOREIGN_KEYS": "false"})
    def test_foreign_keys_disabled_from_env(self) -> None:
        """Test disabling foreign keys from environment."""
        config = DatabaseConfig()
        assert config.foreign_keys_enabled is False

    @patch.dict(os.environ, {"STOCKBOOK_DB_ROW_FACTORY": "row"})
    def test_row_factory_from_env(self) -> None:
        """Test loading row factory from environment."""
        config = DatabaseConfig()
        assert config.row_factory == "row"

    @patch.dict(
        os.environ,
        {
            "DATABASE_URL": "sqlite:///prod.db",
            "TEST_DATABASE_URL": "sqlite:///test.db",
            "STOCKBOOK_DB_TIMEOUT": "45",
            "STOCKBOOK_DB_FOREIGN_KEYS": "true",
            "STOCKBOOK_DB_ROW_FACTORY": "tuple",
        },
    )
    def test_all_settings_from_env(self) -> None:
        """Test loading all settings from environment."""
        config = DatabaseConfig()
        assert config.database_url == "sqlite:///prod.db"
        assert config.test_database_url == "sqlite:///test.db"
        assert config.connection_timeout == 45
        assert config.foreign_keys_enabled is True
        assert config.row_factory == "tuple"


class TestPathExtraction:
    """Test SQLite URL path extraction."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        DatabaseConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        DatabaseConfig.reset()

    def test_extract_path_from_relative_url(self) -> None:
        """Test extracting path from relative SQLite URL."""
        config = DatabaseConfig()
        path = config.extract_path_from_url("sqlite:///data/test.db")
        assert path == Path("data/test.db")

    def test_extract_path_from_absolute_url(self) -> None:
        """Test extracting path from absolute SQLite URL."""
        config = DatabaseConfig()
        path = config.extract_path_from_url("sqlite:////tmp/test.db")
        assert path == Path("/tmp/test.db")

    def test_extract_path_from_memory_url(self) -> None:
        """Test extracting path from in-memory URL."""
        config = DatabaseConfig()
        path = config.extract_path_from_url("sqlite:///:memory:")
        assert path == Path(":memory:")

    def test_extract_path_invalid_url_raises(self) -> None:
        """Test that invalid URL raises ValueError."""
        config = DatabaseConfig()
        with pytest.raises(ValueError, match="Unsupported database URL format"):
            _ = config.extract_path_from_url("postgresql://localhost/db")

    def test_extract_path_empty_url_raises(self) -> None:
        """Test that empty URL raises ValueError."""
        config = DatabaseConfig()
        with pytest.raises(ValueError, match="Unsupported database URL format"):
            _ = config.extract_path_from_url("")

    @patch.dict(os.environ, {"DATABASE_URL": "sqlite:///custom/main.db"})
    def test_db_path_property_with_custom_url(self) -> None:
        """Test db_path property with custom URL."""
        config = DatabaseConfig()
        assert config.db_path == Path("custom/main.db")

    @patch.dict(os.environ, {"TEST_DATABASE_URL": "sqlite:///custom/test.db"})
    def test_test_db_path_property_with_custom_url(self) -> None:
        """Test test_db_path property with custom URL."""
        config = DatabaseConfig()
        assert config.test_db_path == Path("custom/test.db")

    def test_inheritance_from_base_config(self) -> None:
        """Test that DatabaseConfig inherits BaseConfig methods."""
        config = DatabaseConfig()

        # Should have access to BaseConfig static methods
        assert hasattr(config, "get_env_str")
        assert hasattr(config, "get_env_int")
        assert hasattr(config, "get_env_float")
        assert hasattr(config, "get_env_bool")
        assert hasattr(config, "get_env_list")
