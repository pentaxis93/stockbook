"""Presentation layer display configuration.

This module contains formatting, display preferences, and UI-related
configuration for the presentation layer.
"""

from datetime import datetime

from src.shared.config.base import BaseConfig, ValidationError


class DisplayConfig(BaseConfig):
    """Configuration for display and formatting preferences."""

    _instance = None
    _initialized = False

    def __new__(cls) -> "DisplayConfig":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize display configuration."""
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
        """Load display preferences."""
        self._setup_formatting()
        self._setup_pagination()

    def _setup_formatting(self) -> None:
        """Setup formatting preferences."""
        self.date_format = self.get_env_str("STOCKBOOK_DATE_FORMAT", "%Y-%m-%d")
        self.datetime_format = self.get_env_str(
            "STOCKBOOK_DATETIME_FORMAT",
            "%Y-%m-%d %H:%M:%S",
        )
        self.currency_symbol = self.get_env_str("STOCKBOOK_CURRENCY_SYMBOL", "$")
        self.decimal_places = self.get_env_int("STOCKBOOK_DECIMAL_PLACES", 2)

    def _setup_pagination(self) -> None:
        """Setup pagination and table display settings."""
        self.table_page_size = self.get_env_int("STOCKBOOK_TABLE_PAGE_SIZE", 20)
        self.max_rows_display = self.get_env_int("STOCKBOOK_MAX_ROWS_DISPLAY", 100)

    def validate(self) -> None:
        """Validate display configuration.

        Raises:
            ValidationError: If any configuration value is invalid
        """
        if self.decimal_places < 0:
            msg = "decimal_places must be non-negative"
            raise ValidationError(msg)
        if self.table_page_size <= 0:
            msg = "table_page_size must be positive"
            raise ValidationError(msg)
        if self.max_rows_display < self.table_page_size:
            msg = "max_rows_display must be >= table_page_size"
            raise ValidationError(msg)

    def format_currency(self, amount: float) -> str:
        """Format amount as currency string."""
        formatted = f"{amount:,.{self.decimal_places}f}"
        return f"{self.currency_symbol}{formatted}"

    def format_date(self, date_obj: datetime) -> str:
        """Format date according to configured format."""
        return date_obj.strftime(self.date_format)

    def format_datetime(self, datetime_obj: datetime) -> str:
        """Format datetime according to configured format."""
        return datetime_obj.strftime(self.datetime_format)


# Global display config instance
display_config = DisplayConfig()
