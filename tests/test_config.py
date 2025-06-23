"""
Test suite for configuration management system.

This module tests the centralized configuration system that provides:
- Database connection settings
- File paths
- Constants and display preferences
- Date format standards
- Validation rules
- Feature flags

Following TDD approach - tests are written first to define expected behavior.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterator
from unittest.mock import patch

import pytest

# Import the config module (will fail initially - that's expected in TDD)
try:
    from config import Config, ConfigError, ValidationError
except ImportError:
    # This is expected during TDD - we haven't created the module yet
    pytest.skip("Config module not yet implemented", allow_module_level=True)


@pytest.fixture(autouse=True)
def reset_config() -> Iterator[None]:
    """Reset config singleton before each test."""
    Config.reset()
    yield
    Config.reset()


class TestConfigInitialization:
    """Test configuration system initialization and validation."""

    def test_config_loads_default_values(self) -> None:
        """Test that Config loads with sensible defaults."""
        config = Config()

        # Database configuration
        assert config.db_path == Path("database/stockbook.db")
        assert config.schema_path == Path("database/schema.sql")
        assert config.test_db_path == Path("database/test_stockbook.db")

        # File paths
        assert config.app_name == "StockBook"
        assert config.data_dir == Path("data")
        assert config.backup_dir == Path("backups")
        assert config.logs_dir == Path("logs")

        # Display preferences
        assert config.date_format == "%Y-%m-%d"
        assert config.datetime_format == "%Y-%m-%d %H:%M:%S"
        assert config.currency_symbol == "$"
        assert config.decimal_places == 2

    def test_config_validates_on_startup(self) -> None:
        """Test that configuration validation happens on initialization."""
        # This should not raise any exceptions with default config
        config = Config()
        config.validate()

    def test_config_singleton_behavior(self) -> None:
        """Test that Config behaves as a singleton."""
        config1 = Config()
        config2 = Config()

        # Should be the same instance
        assert config1 is config2

    def test_config_loads_from_environment(self) -> None:
        """Test that Config can load values from environment variables."""
        with patch.dict(
            os.environ,
            {
                "STOCKBOOK_DB_PATH": "custom/path/stockbook.db",
                "STOCKBOOK_DATE_FORMAT": "%m/%d/%Y",
                "STOCKBOOK_MAX_POSITIONS": "15",
            },
        ):
            config = Config()

            assert str(config.db_path) == "custom/path/stockbook.db"
            assert config.date_format == "%m/%d/%Y"
            assert config.portfolio_defaults["max_positions"] == 15


class TestDatabaseConfiguration:
    """Test database-related configuration."""

    def test_database_connection_settings(self) -> None:
        """Test database connection configuration."""
        config = Config()

        # Connection settings
        assert config.db_connection_timeout == 30
        assert config.db_foreign_keys_enabled is True
        assert config.db_row_factory == "dict"

    def test_database_paths_are_path_objects(self) -> None:
        """Test that database paths are Path objects."""
        config = Config()

        assert isinstance(config.db_path, Path)
        assert isinstance(config.schema_path, Path)
        assert isinstance(config.test_db_path, Path)

    def test_database_directory_creation(self) -> None:
        """Test that database directory gets created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / "custom_db" / "stockbook.db"

            config = Config()
            config.db_path = custom_path
            config.ensure_directories()

            assert custom_path.parent.exists()


class TestValidationRules:
    """Test validation rule configuration."""

    def test_stock_symbol_validation_rules(self) -> None:
        """Test stock symbol validation configuration."""
        config = Config()

        # Stock symbol validation
        assert hasattr(config, "stock_symbol_pattern")
        assert hasattr(config, "stock_symbol_max_length")
        assert config.stock_symbol_max_length == 10

        # Test the regex pattern is valid
        import re

        pattern = re.compile(config.stock_symbol_pattern)
        assert pattern.match("AAPL") is not None
        assert pattern.match("BRK.B") is not None
        assert pattern.match("123invalid") is None

    def test_grade_validation_rules(self) -> None:
        """Test stock grade validation configuration."""
        config = Config()

        assert hasattr(config, "valid_grades")
        assert set(config.valid_grades) == {"A", "B", "C"}

    def test_transaction_validation_rules(self) -> None:
        """Test transaction validation configuration."""
        config = Config()

        assert hasattr(config, "valid_transaction_types")
        assert set(config.valid_transaction_types) == {"buy", "sell"}

        assert hasattr(config, "min_price")
        assert hasattr(config, "max_price")
        assert config.min_price > 0
        assert config.max_price > config.min_price

        assert hasattr(config, "min_quantity")
        assert hasattr(config, "max_quantity")
        assert config.min_quantity > 0

    def test_portfolio_validation_rules(self) -> None:
        """Test portfolio validation configuration."""
        config = Config()

        assert hasattr(config, "portfolio_name_max_length")
        assert config.portfolio_name_max_length > 0

        assert hasattr(config, "max_risk_per_trade_limit")
        assert 0 < config.max_risk_per_trade_limit <= 100


class TestPortfolioDefaults:
    """Test portfolio default configuration."""

    def test_portfolio_default_values(self) -> None:
        """Test portfolio default configuration values."""
        config = Config()

        defaults = config.portfolio_defaults
        assert isinstance(defaults, dict)

        assert defaults["max_positions"] == 10
        assert defaults["max_risk_per_trade"] == 2.0
        assert "name_prefix" in defaults

    def test_portfolio_defaults_are_valid(self) -> None:
        """Test that portfolio defaults pass validation rules."""
        config = Config()
        defaults = config.portfolio_defaults

        # Max positions should be reasonable
        max_positions = defaults["max_positions"]
        assert isinstance(max_positions, int)
        assert 1 <= max_positions <= 100

        # Risk per trade should be reasonable percentage
        max_risk_per_trade = defaults["max_risk_per_trade"]
        assert isinstance(max_risk_per_trade, (int, float))
        assert 0 < max_risk_per_trade <= config.max_risk_per_trade_limit


class TestFeatureFlags:
    """Test feature flag configuration."""

    def test_feature_flags_exist(self) -> None:
        """Test that feature flags are properly configured."""
        config = Config()

        assert hasattr(config, "features")
        features = config.features

        # Core features
        assert "stock_management" in features
        assert "portfolio_management" in features
        assert "transaction_recording" in features

        # Advanced features (should be disabled by default)
        assert "target_management" in features
        assert "journal_system" in features
        assert "analytics" in features

    def test_development_features_disabled_by_default(self) -> None:
        """Test that development features are disabled by default."""
        config = Config()

        # These should be False in production/default config
        assert config.features["target_management"] is False
        assert config.features["journal_system"] is False
        assert config.features["analytics"] is False

        # These should be enabled (core functionality)
        assert config.features["stock_management"] is True
        assert config.features["portfolio_management"] is True
        assert config.features["transaction_recording"] is True


class TestDateTimeConfiguration:
    """Test date and time format configuration."""

    def test_date_format_configuration(self) -> None:
        """Test date format settings."""
        config = Config()

        # Test formats are valid Python datetime formats
        test_date = datetime(2023, 12, 25, 15, 30, 45)

        formatted_date = test_date.strftime(config.date_format)
        formatted_datetime = test_date.strftime(config.datetime_format)

        assert formatted_date == "2023-12-25"
        assert formatted_datetime == "2023-12-25 15:30:45"

    def test_business_day_configuration(self) -> None:
        """Test business day calculation settings."""
        config = Config()

        assert hasattr(config, "business_days")
        assert set(config.business_days) == {0, 1, 2, 3, 4}  # Monday through Friday

        assert hasattr(config, "market_holidays")
        assert isinstance(config.market_holidays, list)


class TestDisplayConfiguration:
    """Test display and UI configuration."""

    def test_currency_formatting(self) -> None:
        """Test currency display configuration."""
        config = Config()

        assert config.currency_symbol == "$"
        assert config.decimal_places == 2

        # Test formatting method if it exists
        if hasattr(config, "format_currency"):
            assert config.format_currency(1234.567) == "$1,234.57"
            assert config.format_currency(0) == "$0.00"

    def test_table_display_settings(self) -> None:
        """Test table display configuration."""
        config = Config()

        assert hasattr(config, "table_page_size")
        assert config.table_page_size > 0

        assert hasattr(config, "max_rows_display")
        assert config.max_rows_display >= config.table_page_size


class TestConfigValidation:
    """Test configuration validation and error handling."""

    def test_validate_raises_on_invalid_paths(self) -> None:
        """Test validation fails for invalid file paths."""
        config = Config()

        # Set invalid schema path
        config.schema_path = Path("/nonexistent/path/schema.sql")

        with pytest.raises(ValidationError, match="Schema file does not exist"):
            config.validate()

    def test_validate_raises_on_invalid_values(self) -> None:
        """Test validation fails for invalid configuration values."""
        config = Config()

        # Invalid decimal places
        config.decimal_places = -1
        with pytest.raises(
            ValidationError, match="decimal_places must be non-negative"
        ):
            config.validate(skip_file_checks=True)

        # Invalid max positions
        config.decimal_places = 2  # Reset to valid
        config.portfolio_defaults["max_positions"] = 0
        with pytest.raises(ValidationError, match="max_positions must be positive"):
            config.validate(skip_file_checks=True)

    def test_validate_raises_on_invalid_patterns(self) -> None:
        """Test validation fails for invalid regex patterns."""
        config = Config()

        # Invalid regex pattern
        config.stock_symbol_pattern = "[invalid"

        with pytest.raises(ValidationError, match="Invalid regex pattern"):
            config.validate(skip_file_checks=True)


class TestConfigEnvironmentOverrides:
    """Test environment variable configuration overrides."""

    def test_environment_variables_override_defaults(self) -> None:
        """Test that environment variables properly override defaults."""
        env_vars = {
            "STOCKBOOK_CURRENCY_SYMBOL": "€",
            "STOCKBOOK_DECIMAL_PLACES": "3",
            "STOCKBOOK_TABLE_PAGE_SIZE": "25",
        }

        with patch.dict(os.environ, env_vars):
            config = Config()

            assert config.currency_symbol == "€"
            assert config.decimal_places == 3
            assert config.table_page_size == 25

    def test_invalid_environment_values_raise_errors(self) -> None:
        """Test that invalid environment values raise appropriate errors."""
        with patch.dict(
            os.environ, {"STOCKBOOK_DECIMAL_PLACES": "invalid"}
        ), pytest.raises(ConfigError, match="Invalid integer value"):
            _ = Config()


class TestConfigMethods:
    """Test configuration utility methods."""

    def test_get_db_connection_string(self) -> None:
        """Test database connection string generation."""
        config = Config()

        conn_str = config.get_db_connection_string()
        assert str(config.db_path) in conn_str

    def test_ensure_directories_creates_paths(self) -> None:
        """Test that ensure_directories creates necessary directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config()

            # Set paths to temporary locations
            config.data_dir = Path(temp_dir) / "data"
            config.backup_dir = Path(temp_dir) / "backups"
            config.logs_dir = Path(temp_dir) / "logs"

            config.ensure_directories()

            assert config.data_dir.exists()
            assert config.backup_dir.exists()
            assert config.logs_dir.exists()

    def test_is_feature_enabled(self) -> None:
        """Test feature flag checking method."""
        config = Config()

        assert config.is_feature_enabled("stock_management") is True
        assert config.is_feature_enabled("nonexistent_feature") is False

    def test_get_validation_rules(self) -> None:
        """Test validation rules retrieval."""
        config = Config()

        stock_rules = config.get_validation_rules("stock")
        assert "symbol_pattern" in stock_rules
        assert "valid_grades" in stock_rules

        portfolio_rules = config.get_validation_rules("portfolio")
        assert "name_max_length" in portfolio_rules
        assert "max_risk_limit" in portfolio_rules


class TestConfigIntegration:
    """Test configuration integration with other system components."""

    def test_config_integrates_with_database_module(self) -> None:
        """Test that config works with database utilities."""
        # This test will be more meaningful once we refactor database.py
        config = Config()

        # Verify paths are accessible
        assert config.db_path.name == "stockbook.db"
        assert config.schema_path.name == "schema.sql"
