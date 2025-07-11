"""Tests for domain validation rules configuration."""

import os
from unittest.mock import patch

import pytest

from src.domain.config import ValidationRulesConfig, validation_rules_config
from src.shared.config import ValidationError


class TestValidationRulesConfigSingleton:
    """Test ValidationRulesConfig singleton behavior."""

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        ValidationRulesConfig.reset()

    def test_validation_rules_config_singleton(self) -> None:
        """Test that ValidationRulesConfig implements singleton pattern."""
        config1 = ValidationRulesConfig()
        config2 = ValidationRulesConfig()
        assert config1 is config2

    def test_validation_rules_global_instance(self) -> None:
        """Test that global instance uses singleton pattern."""
        assert isinstance(validation_rules_config, ValidationRulesConfig)
        new_config = ValidationRulesConfig()
        assert new_config is ValidationRulesConfig()

    def test_reset_creates_new_instance(self) -> None:
        """Test that reset allows creating new instance."""
        config1 = ValidationRulesConfig()
        ValidationRulesConfig.reset()
        config2 = ValidationRulesConfig()
        assert config1 is not config2

    def test_multiple_init_calls_safe(self) -> None:
        """Test that multiple __init__ calls don't reinitialize."""
        config = ValidationRulesConfig()
        original_pattern = config.stock_symbol_pattern

        # Manually call __init__ again
        config.__init__()

        # Should still have same values
        assert config.stock_symbol_pattern == original_pattern


class TestValidationRulesDefaults:
    """Test default validation rules."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        ValidationRulesConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        ValidationRulesConfig.reset()

    def test_default_stock_validation_rules(self) -> None:
        """Test default stock validation rules."""
        config = ValidationRulesConfig()
        assert config.stock_symbol_pattern == r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$"
        assert config.stock_symbol_max_length == 10
        assert config.valid_grades == ["A", "B", "C"]

    def test_default_portfolio_validation_rules(self) -> None:
        """Test default portfolio validation rules."""
        config = ValidationRulesConfig()
        assert config.portfolio_name_max_length == 100
        assert config.max_risk_per_trade_limit == 10.0

    def test_default_transaction_validation_rules(self) -> None:
        """Test default transaction validation rules."""
        config = ValidationRulesConfig()
        assert config.valid_transaction_types == ["buy", "sell"]
        assert config.min_price == 0.01
        assert config.max_price == 100000.0
        assert config.min_quantity == 1
        assert config.max_quantity == 1000000


class TestValidationRulesEnvironment:
    """Test environment variable handling."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        ValidationRulesConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        ValidationRulesConfig.reset()

    @patch.dict(os.environ, {"STOCKBOOK_SYMBOL_PATTERN": r"^[A-Z]{1,4}$"})
    def test_stock_symbol_pattern_from_env(self) -> None:
        """Test loading stock symbol pattern from environment."""
        config = ValidationRulesConfig()
        assert config.stock_symbol_pattern == r"^[A-Z]{1,4}$"

    @patch.dict(os.environ, {"STOCKBOOK_SYMBOL_MAX_LENGTH": "20"})
    def test_stock_symbol_max_length_from_env(self) -> None:
        """Test loading symbol max length from environment."""
        config = ValidationRulesConfig()
        assert config.stock_symbol_max_length == 20

    @patch.dict(os.environ, {"STOCKBOOK_VALID_GRADES": "A+,A,A-,B+,B,B-"})
    def test_valid_grades_from_env(self) -> None:
        """Test loading valid grades from environment."""
        config = ValidationRulesConfig()
        assert config.valid_grades == ["A+", "A", "A-", "B+", "B", "B-"]

    @patch.dict(os.environ, {"STOCKBOOK_MIN_PRICE": "0.001"})
    def test_min_price_from_env(self) -> None:
        """Test loading min price from environment."""
        config = ValidationRulesConfig()
        assert config.min_price == 0.001

    @patch.dict(os.environ, {"STOCKBOOK_MAX_PRICE": "1000000.0"})
    def test_max_price_from_env(self) -> None:
        """Test loading max price from environment."""
        config = ValidationRulesConfig()
        assert config.max_price == 1000000.0

    @patch.dict(os.environ, {"STOCKBOOK_TRANSACTION_TYPES": "buy,sell,short,cover"})
    def test_transaction_types_from_env(self) -> None:
        """Test loading transaction types from environment."""
        config = ValidationRulesConfig()
        assert config.valid_transaction_types == ["buy", "sell", "short", "cover"]


class TestValidationRulesValidation:
    """Test validation rules validation."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        ValidationRulesConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        ValidationRulesConfig.reset()

    def test_validate_passes_with_defaults(self) -> None:
        """Test that validation passes with default values."""
        config = ValidationRulesConfig()
        config.validate()  # Should not raise

    @patch.dict(os.environ, {"STOCKBOOK_MIN_PRICE": "0"})
    def test_validate_fails_min_price_zero(self) -> None:
        """Test validation fails when min_price is zero."""
        with pytest.raises(ValidationError, match="min_price must be positive"):
            _ = ValidationRulesConfig()

    @patch.dict(os.environ, {"STOCKBOOK_MIN_PRICE": "-1"})
    def test_validate_fails_min_price_negative(self) -> None:
        """Test validation fails when min_price is negative."""
        with pytest.raises(ValidationError, match="min_price must be positive"):
            _ = ValidationRulesConfig()

    @patch.dict(os.environ, {"STOCKBOOK_MIN_PRICE": "100", "STOCKBOOK_MAX_PRICE": "50"})
    def test_validate_fails_max_price_less_than_min(self) -> None:
        """Test validation fails when max_price <= min_price."""
        with pytest.raises(
            ValidationError,
            match="max_price must be greater than min_price",
        ):
            _ = ValidationRulesConfig()

    @patch.dict(os.environ, {"STOCKBOOK_MIN_QUANTITY": "0"})
    def test_validate_fails_min_quantity_zero(self) -> None:
        """Test validation fails when min_quantity is zero."""
        with pytest.raises(ValidationError, match="min_quantity must be positive"):
            _ = ValidationRulesConfig()

    @patch.dict(
        os.environ,
        {"STOCKBOOK_MIN_QUANTITY": "100", "STOCKBOOK_MAX_QUANTITY": "50"},
    )
    def test_validate_fails_max_quantity_less_than_min(self) -> None:
        """Test validation fails when max_quantity <= min_quantity."""
        with pytest.raises(
            ValidationError,
            match="max_quantity must be greater than min_quantity",
        ):
            _ = ValidationRulesConfig()

    @patch.dict(os.environ, {"STOCKBOOK_SYMBOL_MAX_LENGTH": "0"})
    def test_validate_fails_symbol_max_length_zero(self) -> None:
        """Test validation fails when symbol_max_length is zero."""
        with pytest.raises(
            ValidationError,
            match="stock_symbol_max_length must be positive",
        ):
            _ = ValidationRulesConfig()

    @patch.dict(os.environ, {"STOCKBOOK_PORTFOLIO_NAME_MAX_LENGTH": "0"})
    def test_validate_fails_portfolio_name_max_length_zero(self) -> None:
        """Test validation fails when portfolio_name_max_length is zero."""
        with pytest.raises(
            ValidationError,
            match="portfolio_name_max_length must be positive",
        ):
            _ = ValidationRulesConfig()

    @patch.dict(os.environ, {"STOCKBOOK_MAX_RISK_LIMIT": "0"})
    def test_validate_fails_max_risk_limit_zero(self) -> None:
        """Test validation fails when max_risk_per_trade_limit is zero."""
        with pytest.raises(
            ValidationError,
            match="max_risk_per_trade_limit must be positive",
        ):
            _ = ValidationRulesConfig()

    @patch.dict(os.environ, {"STOCKBOOK_SYMBOL_PATTERN": "[invalid regex"})
    def test_validate_fails_invalid_regex_pattern(self) -> None:
        """Test validation fails with invalid regex pattern."""
        with pytest.raises(
            ValidationError,
            match="Invalid regex pattern for stock symbols",
        ):
            _ = ValidationRulesConfig()

    def test_inheritance_from_base_config(self) -> None:
        """Test that ValidationRulesConfig inherits BaseConfig methods."""
        config = ValidationRulesConfig()

        # Should have access to BaseConfig static methods
        assert hasattr(config, "get_env_str")
        assert hasattr(config, "get_env_int")
        assert hasattr(config, "get_env_float")
        assert hasattr(config, "get_env_bool")
        assert hasattr(config, "get_env_list")
