"""Tests for infrastructure paths configuration."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.infrastructure.config import PathsConfig, paths_config


class TestPathsConfigSingleton:
    """Test paths configuration singleton behavior."""

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        PathsConfig.reset()

    def test_paths_config_singleton(self) -> None:
        """Test that PathsConfig implements singleton pattern."""
        config1 = PathsConfig()
        config2 = PathsConfig()
        assert config1 is config2

    def test_paths_config_global_instance(self) -> None:
        """Test that global instance uses singleton pattern."""
        assert isinstance(paths_config, PathsConfig)
        new_config = PathsConfig()
        assert new_config is PathsConfig()

    def test_reset_creates_new_instance(self) -> None:
        """Test that reset allows creating new instance."""
        config1 = PathsConfig()
        PathsConfig.reset()
        config2 = PathsConfig()
        assert config1 is not config2

    def test_multiple_init_calls_safe(self) -> None:
        """Test that multiple __init__ calls don't reinitialize."""
        config = PathsConfig()
        original_data_dir = config.data_dir

        # Manually call __init__ again
        config.__init__()

        # Should still have same values
        assert config.data_dir == original_data_dir


class TestPathsConfigDefaults:
    """Test default paths configuration values."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        PathsConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        PathsConfig.reset()

    def test_default_paths(self) -> None:
        """Test default directory paths."""
        config = PathsConfig()
        assert config.data_dir == Path("data")
        assert config.backup_dir == Path("data/backups")
        assert config.logs_dir == Path("data/logs")

    def test_paths_are_path_objects(self) -> None:
        """Test that all paths are Path objects."""
        config = PathsConfig()
        assert isinstance(config.data_dir, Path)
        assert isinstance(config.backup_dir, Path)
        assert isinstance(config.logs_dir, Path)


class TestPathsConfigEnvironment:
    """Test environment variable handling."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        PathsConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        PathsConfig.reset()

    @patch.dict(os.environ, {"STOCKBOOK_DATA_DIR": "/custom/data"})
    def test_data_dir_from_env(self) -> None:
        """Test loading data directory from environment."""
        config = PathsConfig()
        assert config.data_dir == Path("/custom/data")

    @patch.dict(os.environ, {"STOCKBOOK_BACKUP_DIR": "/custom/backups"})
    def test_backup_dir_from_env(self) -> None:
        """Test loading backup directory from environment."""
        config = PathsConfig()
        assert config.backup_dir == Path("/custom/backups")

    @patch.dict(os.environ, {"STOCKBOOK_LOGS_DIR": "/custom/logs"})
    def test_logs_dir_from_env(self) -> None:
        """Test loading logs directory from environment."""
        config = PathsConfig()
        assert config.logs_dir == Path("/custom/logs")

    @patch.dict(
        os.environ,
        {
            "STOCKBOOK_DATA_DIR": "/app/data",
            "STOCKBOOK_BACKUP_DIR": "/app/backups",
            "STOCKBOOK_LOGS_DIR": "/app/logs",
        },
    )
    def test_all_paths_from_env(self) -> None:
        """Test loading all paths from environment."""
        config = PathsConfig()
        assert config.data_dir == Path("/app/data")
        assert config.backup_dir == Path("/app/backups")
        assert config.logs_dir == Path("/app/logs")


class TestEnsureDirectories:
    """Test directory creation functionality."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        PathsConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        PathsConfig.reset()

    @patch("src.infrastructure.config.paths_config.Path.mkdir")
    def test_ensure_directories_creates_all_dirs(self, mock_mkdir: MagicMock) -> None:
        """Test that ensure_directories creates all required directories."""
        config = PathsConfig()

        # Mock the database config to avoid circular import issues
        with patch("src.infrastructure.config.database_config") as mock_db_config:
            mock_db_config.db_path = Path("data/database/stockbook.db")

            config.ensure_directories()

            # Should create 4 directories
            assert mock_mkdir.call_count == 4

            # Check that mkdir was called with correct arguments
            mock_mkdir.assert_any_call(parents=True, exist_ok=True)

    @patch("src.infrastructure.config.paths_config.Path.mkdir")
    def test_ensure_directories_skips_memory_db(self, mock_mkdir: MagicMock) -> None:
        """Test that ensure_directories skips in-memory database path."""
        config = PathsConfig()

        # Mock the database config with in-memory database
        with patch("src.infrastructure.config.database_config") as mock_db_config:
            mock_db_config.db_path = Path(":memory:")

            config.ensure_directories()

            # Should only create 3 directories (not the :memory: parent)
            assert mock_mkdir.call_count == 3

    @patch("src.infrastructure.config.paths_config.Path.mkdir")
    def test_ensure_directories_with_custom_paths(self, mock_mkdir: MagicMock) -> None:
        """Test ensure_directories with custom environment paths."""
        with patch.dict(
            os.environ,
            {
                "STOCKBOOK_DATA_DIR": "/custom/data",
                "STOCKBOOK_BACKUP_DIR": "/custom/backups",
                "STOCKBOOK_LOGS_DIR": "/custom/logs",
            },
        ):
            PathsConfig.reset()
            config = PathsConfig()

            # Mock the database config
            with patch("src.infrastructure.config.database_config") as mock_db_config:
                mock_db_config.db_path = Path("/custom/db/app.db")

                config.ensure_directories()

                # Should create 4 directories with custom paths
                assert mock_mkdir.call_count == 4

    def test_inheritance_from_base_config(self) -> None:
        """Test that PathsConfig inherits BaseConfig methods."""
        config = PathsConfig()

        # Should have access to BaseConfig static methods
        assert hasattr(config, "get_env_str")
        assert hasattr(config, "get_env_int")
        assert hasattr(config, "get_env_float")
        assert hasattr(config, "get_env_bool")
        assert hasattr(config, "get_env_list")
