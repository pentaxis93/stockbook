"""Configuration for domain validation rules."""

import re

from src.shared.config.base import BaseConfig, ValidationError


class ValidationRulesConfig(BaseConfig):
    """Configuration for domain validation rules."""

    _instance = None
    _initialized = False

    def __new__(cls) -> "ValidationRulesConfig":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize validation rules configuration."""
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
        self._setup_stock_validation()
        self._setup_portfolio_validation()
        self._setup_transaction_validation()
        self._validate_patterns()
        self.validate()

    def _setup_stock_validation(self) -> None:
        """Setup stock validation rules."""
        self.stock_symbol_pattern = self.get_env_str(
            "STOCKBOOK_SYMBOL_PATTERN",
            r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$",
        )
        self.stock_symbol_max_length = self.get_env_int(
            "STOCKBOOK_SYMBOL_MAX_LENGTH",
            10,
        )
        self.valid_grades = self.get_env_list(
            "STOCKBOOK_VALID_GRADES",
            ["A", "B", "C"],
        )

    def _setup_portfolio_validation(self) -> None:
        """Setup portfolio validation rules."""
        self.portfolio_name_max_length = self.get_env_int(
            "STOCKBOOK_PORTFOLIO_NAME_MAX_LENGTH",
            100,
        )
        self.max_risk_per_trade_limit = self.get_env_float(
            "STOCKBOOK_MAX_RISK_LIMIT",
            10.0,
        )

    def _setup_transaction_validation(self) -> None:
        """Setup transaction validation rules."""
        self.valid_transaction_types = self.get_env_list(
            "STOCKBOOK_TRANSACTION_TYPES",
            ["buy", "sell"],
        )
        self.min_price = self.get_env_float("STOCKBOOK_MIN_PRICE", 0.01)
        self.max_price = self.get_env_float("STOCKBOOK_MAX_PRICE", 100000.0)
        self.min_quantity = self.get_env_int("STOCKBOOK_MIN_QUANTITY", 1)
        self.max_quantity = self.get_env_int("STOCKBOOK_MAX_QUANTITY", 1000000)

    def _validate_patterns(self) -> None:
        """Validate regex patterns."""
        try:
            _ = re.compile(self.stock_symbol_pattern)
        except re.error as e:
            msg = f"Invalid regex pattern for stock symbols: {e}"
            raise ValidationError(msg) from e

    def validate(self) -> None:
        """Validate configuration settings."""
        self._validate_numeric_values()

    def _validate_numeric_values(self) -> None:
        """Validate numeric configuration values."""
        if self.min_price <= 0:
            msg = "min_price must be positive"
            raise ValidationError(msg)
        if self.max_price <= self.min_price:
            msg = "max_price must be greater than min_price"
            raise ValidationError(msg)
        if self.min_quantity <= 0:
            msg = "min_quantity must be positive"
            raise ValidationError(msg)
        if self.max_quantity <= self.min_quantity:
            msg = "max_quantity must be greater than min_quantity"
            raise ValidationError(msg)
        if self.stock_symbol_max_length <= 0:
            msg = "stock_symbol_max_length must be positive"
            raise ValidationError(msg)
        if self.portfolio_name_max_length <= 0:
            msg = "portfolio_name_max_length must be positive"
            raise ValidationError(msg)
        if self.max_risk_per_trade_limit <= 0:
            msg = "max_risk_per_trade_limit must be positive"
            raise ValidationError(msg)


# Global validation rules config instance
validation_rules_config = ValidationRulesConfig()
