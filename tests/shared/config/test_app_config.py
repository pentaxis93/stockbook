"""Tests for application-wide configuration."""

import os
from unittest.mock import patch

from src.shared.config import AppConfig, app_config


class TestAppConfigSingleton:
    """Test AppConfig singleton behavior."""

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        AppConfig.reset()

    def test_app_config_singleton(self) -> None:
        """Test that AppConfig implements singleton pattern."""
        config1 = AppConfig()
        config2 = AppConfig()
        assert config1 is config2

    def test_app_config_global_instance(self) -> None:
        """Test that global instance uses singleton pattern."""
        # The global instance should be an AppConfig instance
        assert isinstance(app_config, AppConfig)
        # Creating a new instance should return the same object
        new_config = AppConfig()
        assert new_config is AppConfig()  # Both calls return same instance

    def test_reset_creates_new_instance(self) -> None:
        """Test that reset allows creating new instance."""
        config1 = AppConfig()
        AppConfig.reset()
        config2 = AppConfig()
        assert config1 is not config2

    def test_multiple_init_calls_safe(self) -> None:
        """Test that multiple __init__ calls don't reinitialize."""
        config = AppConfig()
        original_app_name = config.app_name

        # Manually call __init__ again
        config.__init__()

        # Should still have same values
        assert config.app_name == original_app_name


class TestAppConfigDefaults:
    """Test default configuration values."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        AppConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        AppConfig.reset()

    def test_default_app_name(self) -> None:
        """Test default application name."""
        config = AppConfig()
        assert config.app_name == "StockBook"

    def test_default_debug_mode(self) -> None:
        """Test default debug mode is False."""
        config = AppConfig()
        assert config.DEBUG is False

    def test_version_info_loaded(self) -> None:
        """Test that version information is loaded."""
        config = AppConfig()
        assert hasattr(config, "app_version")
        assert hasattr(config, "app_release_date")
        assert hasattr(config, "api_version")

    def test_feature_flags_loaded(self) -> None:
        """Test that feature flags are loaded."""
        config = AppConfig()
        assert hasattr(config, "features")
        assert isinstance(config.features, dict)

    def test_default_core_features_enabled(self) -> None:
        """Test that core features are enabled by default."""
        config = AppConfig()
        assert config.features["stock_management"] is True
        assert config.features["portfolio_management"] is True
        assert config.features["transaction_recording"] is True

    def test_default_advanced_features_disabled(self) -> None:
        """Test that advanced features are disabled by default."""
        config = AppConfig()
        assert config.features["target_management"] is False
        assert config.features["journal_system"] is False
        assert config.features["analytics"] is False

    def test_default_future_features_disabled(self) -> None:
        """Test that future features are disabled by default."""
        config = AppConfig()
        assert config.features["multi_account"] is False
        assert config.features["api_integration"] is False


class TestAppConfigEnvironment:
    """Test environment variable handling."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        AppConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        AppConfig.reset()

    @patch.dict(os.environ, {"STOCKBOOK_APP_NAME": "CustomStockBook"})
    def test_app_name_from_env(self) -> None:
        """Test loading app name from environment."""
        config = AppConfig()
        assert config.app_name == "CustomStockBook"

    @patch.dict(os.environ, {"STOCKBOOK_DEBUG": "true"})
    def test_debug_true_from_env(self) -> None:
        """Test loading debug mode true from environment."""
        config = AppConfig()
        assert config.DEBUG is True

    @patch.dict(os.environ, {"STOCKBOOK_DEBUG": "false"})
    def test_debug_false_from_env(self) -> None:
        """Test loading debug mode false from environment."""
        config = AppConfig()
        assert config.DEBUG is False

    @patch.dict(os.environ, {"STOCKBOOK_FEATURE_STOCKS": "false"})
    def test_disable_core_feature_from_env(self) -> None:
        """Test disabling core feature from environment."""
        config = AppConfig()
        assert config.features["stock_management"] is False

    @patch.dict(os.environ, {"STOCKBOOK_FEATURE_ANALYTICS": "true"})
    def test_enable_advanced_feature_from_env(self) -> None:
        """Test enabling advanced feature from environment."""
        config = AppConfig()
        assert config.features["analytics"] is True

    @patch.dict(
        os.environ,
        {
            "STOCKBOOK_FEATURE_STOCKS": "false",
            "STOCKBOOK_FEATURE_PORTFOLIOS": "false",
            "STOCKBOOK_FEATURE_TRANSACTIONS": "false",
            "STOCKBOOK_FEATURE_TARGETS": "true",
            "STOCKBOOK_FEATURE_JOURNAL": "true",
            "STOCKBOOK_FEATURE_ANALYTICS": "true",
            "STOCKBOOK_FEATURE_MULTI_ACCOUNT": "true",
            "STOCKBOOK_FEATURE_API": "true",
        },
    )
    def test_all_features_from_env(self) -> None:
        """Test loading all feature flags from environment."""
        config = AppConfig()

        # Core features disabled
        assert config.features["stock_management"] is False
        assert config.features["portfolio_management"] is False
        assert config.features["transaction_recording"] is False

        # Advanced features enabled
        assert config.features["target_management"] is True
        assert config.features["journal_system"] is True
        assert config.features["analytics"] is True

        # Future features enabled
        assert config.features["multi_account"] is True
        assert config.features["api_integration"] is True


class TestAppConfigMethods:
    """Test AppConfig methods."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        AppConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        AppConfig.reset()

    def test_is_feature_enabled_existing_enabled(self) -> None:
        """Test checking enabled feature."""
        config = AppConfig()
        assert config.is_feature_enabled("stock_management") is True

    def test_is_feature_enabled_existing_disabled(self) -> None:
        """Test checking disabled feature."""
        config = AppConfig()
        assert config.is_feature_enabled("analytics") is False

    def test_is_feature_enabled_nonexistent(self) -> None:
        """Test checking non-existent feature returns False."""
        config = AppConfig()
        assert config.is_feature_enabled("nonexistent_feature") is False

    def test_get_version_info_structure(self) -> None:
        """Test version info returns correct structure."""
        config = AppConfig()
        version_info = config.get_version_info()

        assert isinstance(version_info, dict)
        assert "version" in version_info
        assert "release_date" in version_info
        assert "api_version" in version_info

    def test_get_version_info_values(self) -> None:
        """Test version info contains actual values."""
        config = AppConfig()
        version_info = config.get_version_info()

        # Check that values match what was loaded
        assert version_info["version"] == config.app_version
        assert version_info["release_date"] == config.app_release_date
        assert version_info["api_version"] == config.api_version

    def test_inheritance_from_base_config(self) -> None:
        """Test that AppConfig inherits BaseConfig methods."""
        config = AppConfig()

        # Should have access to BaseConfig static methods
        assert hasattr(config, "get_env_str")
        assert hasattr(config, "get_env_int")
        assert hasattr(config, "get_env_float")
        assert hasattr(config, "get_env_bool")
        assert hasattr(config, "get_env_list")
