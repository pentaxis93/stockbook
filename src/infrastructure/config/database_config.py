"""Configuration for database connection settings."""

from pathlib import Path

from src.shared.config.base import BaseConfig


class DatabaseConfig(BaseConfig):
    """Configuration for database connection settings."""

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
        """Load all configuration settings."""
        self._setup_database_urls()
        self._setup_connection_settings()

    def _setup_database_urls(self) -> None:
        """Setup database URLs."""
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

    def _setup_connection_settings(self) -> None:
        """Setup connection configuration."""
        self.connection_timeout = self.get_env_int("STOCKBOOK_DB_TIMEOUT", 30)
        self.foreign_keys_enabled = self.get_env_bool(
            "STOCKBOOK_DB_FOREIGN_KEYS",
            default=True,
        )
        self.row_factory = self.get_env_str("STOCKBOOK_DB_ROW_FACTORY", "dict")

    def get_connection_string(self, *, test: bool = False) -> str:
        """Get database connection string.

        Args:
            test: Whether to return test database URL

        Returns:
            Database connection string
        """
        return self.test_database_url if test else self.database_url

    def extract_path_from_url(self, database_url: str) -> Path:
        """Extract file path from SQLite URL.

        Args:
            database_url: SQLite URL (e.g., "sqlite:///path/to/db.db")

        Returns:
            Path object for the database file
        """
        if database_url == "sqlite:///:memory:":
            return Path(":memory:")

        if database_url.startswith("sqlite:///"):
            return Path(database_url.replace("sqlite:///", ""))

        msg = f"Unsupported database URL format: {database_url}"
        raise ValueError(msg)

    @property
    def db_path(self) -> Path:
        """Get database file path."""
        return self.extract_path_from_url(self.database_url)

    @property
    def test_db_path(self) -> Path:
        """Get test database file path."""
        return self.extract_path_from_url(self.test_database_url)


# Global database config instance
database_config = DatabaseConfig()
