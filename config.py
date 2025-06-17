"""
Configuration management system for StockBook.

This module provides centralized configuration management including:
- Database connection settings
- File paths and directories
- Constants and display preferences
- Date format standards
- Validation rules (symbol patterns, grade options)
- Feature flags for development phases

The configuration system supports environment variable overrides and
validates all settings on initialization.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


class ConfigError(Exception):
    """Base exception for configuration errors."""

    pass


class ValidationError(ConfigError):
    """Exception raised when configuration validation fails."""

    pass


class Config:
    """
    Centralized configuration management for StockBook.

    Implements singleton pattern to ensure consistent configuration
    across the application. Supports environment variable overrides
    and comprehensive validation.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize configuration with defaults and environment overrides."""
        if self._initialized:
            return

        self._load_configuration()
        self._initialized = True

    @classmethod
    def reset(cls):
        """Reset singleton for testing purposes."""
        cls._instance = None
        cls._initialized = False

    def _load_configuration(self):
        """Load all configuration settings."""
        # Application settings
        self.app_name = self._get_env_str("STOCKBOOK_APP_NAME", "StockBook")

        # Database configuration
        self.db_path = Path(
            self._get_env_str("STOCKBOOK_DB_PATH", "database/stockbook.db")
        )
        self.schema_path = Path(
            self._get_env_str("STOCKBOOK_SCHEMA_PATH", "database/schema.sql")
        )
        self.test_db_path = Path(
            self._get_env_str("STOCKBOOK_TEST_DB_PATH", "database/test_stockbook.db")
        )

        # Database connection settings
        self.db_connection_timeout = self._get_env_int("STOCKBOOK_DB_TIMEOUT", 30)
        self.db_foreign_keys_enabled = self._get_env_bool(
            "STOCKBOOK_DB_FOREIGN_KEYS", True
        )
        self.db_row_factory = self._get_env_str("STOCKBOOK_DB_ROW_FACTORY", "dict")

        # Directory paths
        self.data_dir = Path(self._get_env_str("STOCKBOOK_DATA_DIR", "data"))
        self.backup_dir = Path(self._get_env_str("STOCKBOOK_BACKUP_DIR", "backups"))
        self.logs_dir = Path(self._get_env_str("STOCKBOOK_LOGS_DIR", "logs"))

        # Display preferences
        self.date_format = self._get_env_str("STOCKBOOK_DATE_FORMAT", "%Y-%m-%d")
        self.datetime_format = self._get_env_str(
            "STOCKBOOK_DATETIME_FORMAT", "%Y-%m-%d %H:%M:%S"
        )
        self.currency_symbol = self._get_env_str("STOCKBOOK_CURRENCY_SYMBOL", "$")
        self.decimal_places = self._get_env_int("STOCKBOOK_DECIMAL_PLACES", 2)

        # Table display settings
        self.table_page_size = self._get_env_int("STOCKBOOK_TABLE_PAGE_SIZE", 20)
        self.max_rows_display = self._get_env_int("STOCKBOOK_MAX_ROWS_DISPLAY", 100)

        # Validation rules
        self._setup_validation_rules()

        # Portfolio defaults
        self._setup_portfolio_defaults()

        # Feature flags
        self._setup_feature_flags()

        # Business day configuration
        self.business_days = {0, 1, 2, 3, 4}  # Monday through Friday
        self.market_holidays = []  # Can be populated from external source

        # Streamlit configuration
        self._setup_streamlit_config()

    def _setup_validation_rules(self):
        """Setup validation rules for different data types."""
        # Stock symbol validation
        self.stock_symbol_pattern = self._get_env_str(
            "STOCKBOOK_SYMBOL_PATTERN", r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$"
        )
        self.stock_symbol_max_length = self._get_env_int(
            "STOCKBOOK_SYMBOL_MAX_LENGTH", 10
        )

        # Valid stock grades
        self.valid_grades = self._get_env_list(
            "STOCKBOOK_VALID_GRADES", ["A", "B", "C"]
        )

        # Transaction validation
        self.valid_transaction_types = self._get_env_list(
            "STOCKBOOK_TRANSACTION_TYPES", ["buy", "sell"]
        )
        self.min_price = self._get_env_float("STOCKBOOK_MIN_PRICE", 0.01)
        self.max_price = self._get_env_float("STOCKBOOK_MAX_PRICE", 100000.0)
        self.min_quantity = self._get_env_int("STOCKBOOK_MIN_QUANTITY", 1)
        self.max_quantity = self._get_env_int("STOCKBOOK_MAX_QUANTITY", 1000000)

        # Portfolio validation
        self.portfolio_name_max_length = self._get_env_int(
            "STOCKBOOK_PORTFOLIO_NAME_MAX_LENGTH", 100
        )
        self.max_risk_per_trade_limit = self._get_env_float(
            "STOCKBOOK_MAX_RISK_LIMIT", 10.0
        )

    def _setup_portfolio_defaults(self):
        """Setup default portfolio configuration."""
        self.portfolio_defaults = {
            "max_positions": self._get_env_int("STOCKBOOK_MAX_POSITIONS", 10),
            "max_risk_per_trade": self._get_env_float(
                "STOCKBOOK_MAX_RISK_PER_TRADE", 2.0
            ),
            "name_prefix": self._get_env_str("STOCKBOOK_PORTFOLIO_PREFIX", "Portfolio"),
        }

    def _setup_feature_flags(self):
        """Setup feature flags for different development phases."""
        self.features = {
            # Core features (Phase 1-2)
            "stock_management": self._get_env_bool("STOCKBOOK_FEATURE_STOCKS", True),
            "portfolio_management": self._get_env_bool(
                "STOCKBOOK_FEATURE_PORTFOLIOS", True
            ),
            "transaction_recording": self._get_env_bool(
                "STOCKBOOK_FEATURE_TRANSACTIONS", True
            ),
            # Advanced features (Phase 3)
            "target_management": self._get_env_bool("STOCKBOOK_FEATURE_TARGETS", False),
            "journal_system": self._get_env_bool("STOCKBOOK_FEATURE_JOURNAL", False),
            "analytics": self._get_env_bool("STOCKBOOK_FEATURE_ANALYTICS", False),
            # Future features (Phase 4)
            "multi_account": self._get_env_bool(
                "STOCKBOOK_FEATURE_MULTI_ACCOUNT", False
            ),
            "api_integration": self._get_env_bool("STOCKBOOK_FEATURE_API", False),
        }

    def _setup_streamlit_config(self):
        """Setup Streamlit-specific configuration."""
        self.streamlit_config = {
            "page_title": self.app_name,
            "page_icon": "📈",
            "layout": "wide",
            "initial_sidebar_state": "expanded",
        }

    def _get_env_str(self, key: str, default: str) -> str:
        """Get string value from environment with default."""
        return os.getenv(key, default)

    def _get_env_int(self, key: str, default: int) -> int:
        """Get integer value from environment with default."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise ConfigError(f"Invalid integer value for {key}: {value}")

    def _get_env_float(self, key: str, default: float) -> float:
        """Get float value from environment with default."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            raise ConfigError(f"Invalid float value for {key}: {value}")

    def _get_env_bool(self, key: str, default: bool) -> bool:
        """Get boolean value from environment with default."""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def _get_env_list(self, key: str, default: List[str]) -> List[str]:
        """Get list value from environment with default."""
        value = os.getenv(key)
        if value is None:
            return default
        return [item.strip() for item in value.split(",")]

    def validate(self, skip_file_checks: bool = False):
        """
        Validate configuration settings.

        Args:
            skip_file_checks: Skip file existence checks (useful for testing)

        Raises:
            ValidationError: If any configuration value is invalid
        """
        self._validate_values()
        self._validate_patterns()
        if not skip_file_checks:
            self._validate_paths()

    def _validate_paths(self):
        """Validate file and directory paths."""
        # Schema file must exist
        if not self.schema_path.exists():
            raise ValidationError(f"Schema file does not exist: {self.schema_path}")

    def _validate_values(self):
        """Validate configuration values."""
        if self.decimal_places < 0:
            raise ValidationError("decimal_places must be non-negative")

        if self.portfolio_defaults["max_positions"] <= 0:
            raise ValidationError("max_positions must be positive")

        if self.min_price <= 0:
            raise ValidationError("min_price must be positive")

        if self.max_price <= self.min_price:
            raise ValidationError("max_price must be greater than min_price")

        if self.min_quantity <= 0:
            raise ValidationError("min_quantity must be positive")

        if self.table_page_size <= 0:
            raise ValidationError("table_page_size must be positive")

        if self.max_rows_display < self.table_page_size:
            raise ValidationError("max_rows_display must be >= table_page_size")

    def _validate_patterns(self):
        """Validate regex patterns."""
        try:
            re.compile(self.stock_symbol_pattern)
        except re.error as e:
            raise ValidationError(f"Invalid regex pattern for stock symbols: {e}")

    def get_db_connection_string(self) -> str:
        """Get database connection string."""
        return f"sqlite:///{self.db_path}"

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.db_path.parent,
            self.data_dir,
            self.backup_dir,
            self.logs_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        return self.features.get(feature_name, False)

    def get_validation_rules(self, entity_type: str) -> Dict[str, Any]:
        """Get validation rules for a specific entity type."""
        if entity_type == "stock":
            return {
                "symbol_pattern": self.stock_symbol_pattern,
                "symbol_max_length": self.stock_symbol_max_length,
                "valid_grades": self.valid_grades,
            }
        elif entity_type == "portfolio":
            return {
                "name_max_length": self.portfolio_name_max_length,
                "max_risk_limit": self.max_risk_per_trade_limit,
            }
        elif entity_type == "transaction":
            return {
                "valid_types": self.valid_transaction_types,
                "min_price": self.min_price,
                "max_price": self.max_price,
                "min_quantity": self.min_quantity,
                "max_quantity": self.max_quantity,
            }
        else:
            return {}

    def format_currency(self, amount: Union[int, float]) -> str:
        """Format amount as currency string."""
        formatted = f"{amount:,.{self.decimal_places}f}"
        return f"{self.currency_symbol}{formatted}"

    def format_date(self, date_obj: datetime) -> str:
        """Format date according to configured format."""
        return date_obj.strftime(self.date_format)

    def format_datetime(self, datetime_obj: datetime) -> str:
        """Format datetime according to configured format."""
        return datetime_obj.strftime(self.datetime_format)


# Global config instance
config = Config()
