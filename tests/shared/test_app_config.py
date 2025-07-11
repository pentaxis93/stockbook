"""Tests for application-wide configuration."""

import pytest

from src.shared.config import AppConfig, app_config


class TestAppConfig:
    """Test application configuration."""

    def test_app_config_singleton(self) -> None:
        """Test that AppConfig implements singleton pattern."""
        config1 = AppConfig()
        config2 = AppConfig()
        assert config1 is config2
        assert config1 is app_config

    def test_app_config_loads_defaults(self) -> None:
        """Test that default values are loaded."""
        assert app_config.app_name == "StockBook"
        assert app_config.DEBUG is False
        
    def test_feature_flags_exist(self) -> None:
        """Test that feature flags are configured."""
        assert "stock_management" in app_config.features
        assert "portfolio_management" in app_config.features
        assert "transaction_recording" in app_config.features

    def test_is_feature_enabled(self) -> None:
        """Test feature flag checking."""
        assert app_config.is_feature_enabled("stock_management") is True
        assert app_config.is_feature_enabled("nonexistent_feature") is False

    def test_version_info(self) -> None:
        """Test version information retrieval."""
        version_info = app_config.get_version_info()
        assert "version" in version_info
        assert "release_date" in version_info
        assert "api_version" in version_info