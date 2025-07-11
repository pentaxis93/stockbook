"""Domain validation rules configuration.

This module contains all validation patterns and rules for domain entities.
"""

import re
from typing import Any

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
        """Load all validation rules."""
        self._setup_stock_validation()
        self._setup_transaction_validation()
        self._setup_portfolio_validation()

    def _setup_stock_validation(self) -> None:
        """Setup stock validation rules."""
        # Stock symbol validation
        self.stock_symbol_pattern = self.get_env_str(
            "STOCKBOOK_SYMBOL_PATTERN",
            r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$",
        )
        self.stock_symbol_max_length = self.get_env_int(
            "STOCKBOOK_SYMBOL_MAX_LENGTH",
            10,
        )

        # Valid stock grades
        self.valid_grades = self.get_env_list(
            "STOCKBOOK_VALID_GRADES",
            ["A", "B", "C"],
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

    def validate(self) -> None:
        """Validate configuration settings.

        Raises:
            ValidationError: If any configuration value is invalid
        """
        self._validate_patterns()
        self._validate_numeric_rules()

    def _validate_patterns(self) -> None:
        """Validate regex patterns."""
        try:
            _ = re.compile(self.stock_symbol_pattern)
        except re.error as e:
            msg = f"Invalid regex pattern for stock symbols: {e}"
            raise ValidationError(msg) from e

    def _validate_numeric_rules(self) -> None:
        """Validate numeric validation rules."""
        if self.min_price <= 0:
            msg = "min_price must be positive"
            raise ValidationError(msg)
        if self.max_price <= self.min_price:
            msg = "max_price must be greater than min_price"
            raise ValidationError(msg)
        if self.min_quantity <= 0:
            msg = "min_quantity must be positive"
            raise ValidationError(msg)

    def get_validation_rules(self, entity_type: str) -> dict[str, Any]:
        """Get validation rules for a specific entity type."""
        validation_rules_map: dict[str, dict[str, Any]] = {
            "stock": {
                "symbol_pattern": self.stock_symbol_pattern,
                "symbol_max_length": self.stock_symbol_max_length,
                "valid_grades": self.valid_grades,
            },
            "portfolio": {
                "name_max_length": self.portfolio_name_max_length,
                "max_risk_limit": self.max_risk_per_trade_limit,
            },
            "transaction": {
                "valid_types": self.valid_transaction_types,
                "min_price": self.min_price,
                "max_price": self.max_price,
                "min_quantity": self.min_quantity,
                "max_quantity": self.max_quantity,
            },
        }
        default: dict[str, Any] = {}
        return validation_rules_map.get(entity_type, default)


# Global validation rules instance
validation_rules = ValidationRulesConfig()
