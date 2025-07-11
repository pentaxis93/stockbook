"""Configuration for file system paths."""

from pathlib import Path

from src.shared.config.base import BaseConfig


class PathsConfig(BaseConfig):
    """Configuration for file system paths."""

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
        """Load all configuration settings."""
        self._setup_paths()

    def _setup_paths(self) -> None:
        """Setup directory paths."""
        self.data_dir = Path(self.get_env_str("STOCKBOOK_DATA_DIR", "data"))
        self.backup_dir = Path(
            self.get_env_str("STOCKBOOK_BACKUP_DIR", "data/backups"),
        )
        self.logs_dir = Path(self.get_env_str("STOCKBOOK_LOGS_DIR", "data/logs"))

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        from src.infrastructure.config import database_config

        directories = [
            database_config.db_path.parent,
            self.data_dir,
            self.backup_dir,
            self.logs_dir,
        ]

        for directory in directories:
            if directory != Path(":memory:").parent:  # Skip in-memory DB
                directory.mkdir(parents=True, exist_ok=True)


# Global paths config instance
paths_config = PathsConfig()
