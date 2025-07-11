"""Infrastructure paths configuration.

This module contains file system paths and directory management
for the infrastructure layer.
"""

from pathlib import Path

from src.shared.config.base import BaseConfig


class PathsConfig(BaseConfig):
    """Configuration for file system paths and directories."""

    _instance = None
    _initialized = False

    def __new__(cls) -> "PathsConfig":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize paths configuration."""
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
        """Load directory paths."""
        self.data_dir = Path(self.get_env_str("STOCKBOOK_DATA_DIR", "data"))
        self.backup_dir = Path(
            self.get_env_str("STOCKBOOK_BACKUP_DIR", "data/backups"),
        )
        self.logs_dir = Path(self.get_env_str("STOCKBOOK_LOGS_DIR", "data/logs"))

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.data_dir,
            self.backup_dir,
            self.logs_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_database_path(self, database_url: str) -> Path:
        """Extract file path from SQLite URL.

        Args:
            database_url: SQLite URL (e.g., "sqlite:///path/to/db.db")

        Returns:
            Path object for the database file
        """
        if database_url == "sqlite:///:memory:":
            return Path(":memory:")

        if database_url.startswith("sqlite:///"):
            path = Path(database_url.replace("sqlite:///", ""))
            # Ensure parent directory exists
            if path.parent and not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            return path

        msg = f"Unsupported database URL format: {database_url}"
        raise ValueError(msg)


# Global paths config instance
paths_config = PathsConfig()
