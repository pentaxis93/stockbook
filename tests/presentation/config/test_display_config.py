"""Tests for presentation display configuration."""

import os
from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from src.presentation.config import DisplayConfig, display_config
from src.shared.config import ValidationError


class TestDisplayConfigSingleton:
    """Test display configuration singleton behavior."""

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        DisplayConfig.reset()

    def test_display_config_singleton(self) -> None:
        """Test that DisplayConfig implements singleton pattern."""
        config1 = DisplayConfig()
        config2 = DisplayConfig()
        assert config1 is config2

    def test_display_config_global_instance(self) -> None:
        """Test that global instance uses singleton pattern."""
        assert isinstance(display_config, DisplayConfig)
        new_config = DisplayConfig()
        assert new_config is DisplayConfig()

    def test_reset_creates_new_instance(self) -> None:
        """Test that reset allows creating new instance."""
        config1 = DisplayConfig()
        DisplayConfig.reset()
        config2 = DisplayConfig()
        assert config1 is not config2

    def test_multiple_init_calls_safe(self) -> None:
        """Test that multiple __init__ calls don't reinitialize."""
        config = DisplayConfig()
        original_date_format = config.date_format

        # Manually call __init__ again
        config.__init__()

        # Should still have same values
        assert config.date_format == original_date_format


class TestDisplayConfigDefaults:
    """Test default display configuration values."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        DisplayConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        DisplayConfig.reset()

    def test_default_date_formats(self) -> None:
        """Test default date and datetime formats."""
        config = DisplayConfig()
        assert config.date_format == "%Y-%m-%d"
        assert config.datetime_format == "%Y-%m-%d %H:%M:%S"

    def test_default_currency_settings(self) -> None:
        """Test default currency display settings."""
        config = DisplayConfig()
        assert config.currency_symbol == "$"
        assert config.decimal_places == 2

    def test_default_table_settings(self) -> None:
        """Test default table display settings."""
        config = DisplayConfig()
        assert config.table_page_size == 20
        assert config.max_rows_display == 100


class TestDisplayConfigEnvironment:
    """Test environment variable handling."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        DisplayConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        DisplayConfig.reset()

    @patch.dict(os.environ, {"STOCKBOOK_DATE_FORMAT": "%d/%m/%Y"})
    def test_date_format_from_env(self) -> None:
        """Test loading date format from environment."""
        config = DisplayConfig()
        assert config.date_format == "%d/%m/%Y"

    @patch.dict(os.environ, {"STOCKBOOK_DATETIME_FORMAT": "%d/%m/%Y %I:%M %p"})
    def test_datetime_format_from_env(self) -> None:
        """Test loading datetime format from environment."""
        config = DisplayConfig()
        assert config.datetime_format == "%d/%m/%Y %I:%M %p"

    @patch.dict(os.environ, {"STOCKBOOK_CURRENCY_SYMBOL": "€"})
    def test_currency_symbol_from_env(self) -> None:
        """Test loading currency symbol from environment."""
        config = DisplayConfig()
        assert config.currency_symbol == "€"

    @patch.dict(os.environ, {"STOCKBOOK_DECIMAL_PLACES": "4"})
    def test_decimal_places_from_env(self) -> None:
        """Test loading decimal places from environment."""
        config = DisplayConfig()
        assert config.decimal_places == 4

    @patch.dict(os.environ, {"STOCKBOOK_TABLE_PAGE_SIZE": "50"})
    def test_table_page_size_from_env(self) -> None:
        """Test loading table page size from environment."""
        config = DisplayConfig()
        assert config.table_page_size == 50

    @patch.dict(os.environ, {"STOCKBOOK_MAX_ROWS_DISPLAY": "200"})
    def test_max_rows_display_from_env(self) -> None:
        """Test loading max rows display from environment."""
        config = DisplayConfig()
        assert config.max_rows_display == 200

    @patch.dict(
        os.environ,
        {
            "STOCKBOOK_DATE_FORMAT": "%m-%d-%Y",
            "STOCKBOOK_DATETIME_FORMAT": "%m-%d-%Y %H:%M",
            "STOCKBOOK_CURRENCY_SYMBOL": "£",
            "STOCKBOOK_DECIMAL_PLACES": "3",
            "STOCKBOOK_TABLE_PAGE_SIZE": "30",
            "STOCKBOOK_MAX_ROWS_DISPLAY": "150",
        },
    )
    def test_all_settings_from_env(self) -> None:
        """Test loading all settings from environment."""
        config = DisplayConfig()
        assert config.date_format == "%m-%d-%Y"
        assert config.datetime_format == "%m-%d-%Y %H:%M"
        assert config.currency_symbol == "£"
        assert config.decimal_places == 3
        assert config.table_page_size == 30
        assert config.max_rows_display == 150


class TestDisplayConfigValidation:
    """Test display configuration validation."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        DisplayConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        DisplayConfig.reset()

    def test_validate_passes_with_defaults(self) -> None:
        """Test that validation passes with default values."""
        _ = DisplayConfig()  # Should not raise

    @patch.dict(os.environ, {"STOCKBOOK_DECIMAL_PLACES": "-1"})
    def test_validate_fails_negative_decimal_places(self) -> None:
        """Test validation fails when decimal_places is negative."""
        with pytest.raises(
            ValidationError,
            match="decimal_places must be non-negative",
        ):
            _ = DisplayConfig()

    @patch.dict(os.environ, {"STOCKBOOK_TABLE_PAGE_SIZE": "0"})
    def test_validate_fails_zero_page_size(self) -> None:
        """Test validation fails when table_page_size is zero."""
        with pytest.raises(ValidationError, match="table_page_size must be positive"):
            _ = DisplayConfig()

    @patch.dict(os.environ, {"STOCKBOOK_TABLE_PAGE_SIZE": "-10"})
    def test_validate_fails_negative_page_size(self) -> None:
        """Test validation fails when table_page_size is negative."""
        with pytest.raises(ValidationError, match="table_page_size must be positive"):
            _ = DisplayConfig()

    @patch.dict(
        os.environ,
        {"STOCKBOOK_TABLE_PAGE_SIZE": "100", "STOCKBOOK_MAX_ROWS_DISPLAY": "50"},
    )
    def test_validate_fails_max_rows_less_than_page_size(self) -> None:
        """Test validation fails when max_rows_display < table_page_size."""
        with pytest.raises(
            ValidationError,
            match="max_rows_display must be >= table_page_size",
        ):
            _ = DisplayConfig()


class TestDisplayConfigFormatting:
    """Test display formatting methods."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        DisplayConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        DisplayConfig.reset()

    def test_format_currency_default(self) -> None:
        """Test currency formatting with default settings."""
        config = DisplayConfig()
        assert config.format_currency(1234.56) == "$1,234.56"
        assert config.format_currency(0.99) == "$0.99"
        assert config.format_currency(1000000.0) == "$1,000,000.00"

    @patch.dict(
        os.environ,
        {"STOCKBOOK_CURRENCY_SYMBOL": "€", "STOCKBOOK_DECIMAL_PLACES": "3"},
    )
    def test_format_currency_custom(self) -> None:
        """Test currency formatting with custom settings."""
        config = DisplayConfig()
        assert config.format_currency(1234.5678) == "€1,234.568"
        assert config.format_currency(0.999) == "€0.999"

    def test_format_date_default(self) -> None:
        """Test date formatting with default format."""
        config = DisplayConfig()
        test_date = datetime(2024, 3, 15, 14, 30, 45, tzinfo=UTC)
        assert config.format_date(test_date) == "2024-03-15"

    @patch.dict(os.environ, {"STOCKBOOK_DATE_FORMAT": "%d/%m/%Y"})
    def test_format_date_custom(self) -> None:
        """Test date formatting with custom format."""
        config = DisplayConfig()
        test_date = datetime(2024, 3, 15, 14, 30, 45, tzinfo=UTC)
        assert config.format_date(test_date) == "15/03/2024"

    def test_format_datetime_default(self) -> None:
        """Test datetime formatting with default format."""
        config = DisplayConfig()
        test_datetime = datetime(2024, 3, 15, 14, 30, 45, tzinfo=UTC)
        assert config.format_datetime(test_datetime) == "2024-03-15 14:30:45"

    @patch.dict(os.environ, {"STOCKBOOK_DATETIME_FORMAT": "%d/%m/%Y %I:%M %p"})
    def test_format_datetime_custom(self) -> None:
        """Test datetime formatting with custom format."""
        config = DisplayConfig()
        test_datetime = datetime(2024, 3, 15, 14, 30, 45, tzinfo=UTC)
        assert config.format_datetime(test_datetime) == "15/03/2024 02:30 PM"

    def test_inheritance_from_base_config(self) -> None:
        """Test that DisplayConfig inherits BaseConfig methods."""
        config = DisplayConfig()

        # Should have access to BaseConfig static methods
        assert hasattr(config, "get_env_str")
        assert hasattr(config, "get_env_int")
        assert hasattr(config, "get_env_float")
        assert hasattr(config, "get_env_bool")
        assert hasattr(config, "get_env_list")
