"""Tests for infrastructure database configuration."""

import pytest

from src.infrastructure.config import DatabaseConfig, database_config


class TestDatabaseConfig:
    """Test database configuration."""

    def test_database_config_singleton(self) -> None:
        """Test that DatabaseConfig implements singleton pattern."""
        config1 = DatabaseConfig()
        config2 = DatabaseConfig()
        assert config1 is config2
        assert config1 is database_config

    def test_database_config_defaults(self) -> None:
        """Test default database configuration values."""
        assert database_config.database_url == "sqlite:///data/database/stockbook.db"
        assert database_config.test_database_url == "sqlite:///:memory:"
        assert database_config.connection_timeout == 30
        assert database_config.foreign_keys_enabled is True
        assert database_config.row_factory == "dict"

    def test_get_connection_string(self) -> None:
        """Test connection string retrieval."""
        # Default should return main database URL
        assert database_config.get_connection_string() == database_config.database_url
        
        # Test mode should return test database URL
        assert database_config.get_connection_string(test=True) == database_config.test_database_url