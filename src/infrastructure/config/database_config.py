"""Infrastructure database configuration.

This module contains database connection settings and configuration
specific to the infrastructure layer.
"""

from src.shared.config.base import BaseConfig


class DatabaseConfig(BaseConfig):
    """Configuration for database connections and settings."""

    _instance = None
    _initialized = False

    def __new__(cls) -> "DatabaseConfig":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize database configuration."""
        if self._initialized:
            return

        self._load_configuration()
        self._initialized = True

    @classmethod
    def reset(cls) -> None:
        """Reset singleton for testing purposes."""
        cls._instance = None
        cls._initialized = False

    def _load_configuration(self) -> None:
        """Load database configuration settings."""
        # Support DATABASE_URL for modern configuration
        self.database_url = self.get_env_str(
            "DATABASE_URL",
            "sqlite:///data/database/stockbook.db",
        )

        # Support TEST_DATABASE_URL for test configuration
        self.test_database_url = self.get_env_str(
            "TEST_DATABASE_URL",
            "sqlite:///:memory:",
        )

        # Connection configuration
        self.connection_timeout = self.get_env_int("STOCKBOOK_DB_TIMEOUT", 30)
        self.foreign_keys_enabled = self.get_env_bool(
            "STOCKBOOK_DB_FOREIGN_KEYS",
            default=True,
        )
        self.row_factory = self.get_env_str("STOCKBOOK_DB_ROW_FACTORY", "dict")

    def get_connection_string(self, *, test: bool = False) -> str:
        """Get database connection string.

        Args:
            test: If True, return test database URL

        Returns:
            Database connection URL string
        """
        return self.test_database_url if test else self.database_url


# Global database config instance
database_config = DatabaseConfig()
