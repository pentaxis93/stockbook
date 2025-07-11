"""Tests for domain business rules configuration."""

import os
from unittest.mock import patch

import pytest

from src.domain.config import BusinessRulesConfig, business_rules_config
from src.shared.config import ValidationError


class TestBusinessRulesConfigSingleton:
    """Test BusinessRulesConfig singleton behavior."""

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        BusinessRulesConfig.reset()

    def test_business_rules_config_singleton(self) -> None:
        """Test that BusinessRulesConfig implements singleton pattern."""
        config1 = BusinessRulesConfig()
        config2 = BusinessRulesConfig()
        assert config1 is config2

    def test_business_rules_global_instance(self) -> None:
        """Test that global instance uses singleton pattern."""
        assert isinstance(business_rules_config, BusinessRulesConfig)
        new_config = BusinessRulesConfig()
        assert new_config is BusinessRulesConfig()

    def test_reset_creates_new_instance(self) -> None:
        """Test that reset allows creating new instance."""
        config1 = BusinessRulesConfig()
        BusinessRulesConfig.reset()
        config2 = BusinessRulesConfig()
        assert config1 is not config2

    def test_multiple_init_calls_safe(self) -> None:
        """Test that multiple __init__ calls don't reinitialize."""
        config = BusinessRulesConfig()
        original_defaults = config.portfolio_defaults.copy()

        # Manually call __init__ again
        config.__init__()

        # Should still have same values
        assert config.portfolio_defaults == original_defaults


class TestBusinessRulesDefaults:
    """Test default business rules."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        BusinessRulesConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        BusinessRulesConfig.reset()

    def test_default_portfolio_defaults(self) -> None:
        """Test default portfolio configuration."""
        config = BusinessRulesConfig()
        assert config.portfolio_defaults["max_positions"] == 10
        assert config.portfolio_defaults["max_risk_per_trade"] == 2.0
        assert config.portfolio_defaults["name_prefix"] == "Portfolio"

    def test_default_business_days(self) -> None:
        """Test default business days configuration."""
        config = BusinessRulesConfig()
        assert config.business_days == {0, 1, 2, 3, 4}  # Monday through Friday
        assert config.market_holidays == []

    def test_is_business_day_weekdays(self) -> None:
        """Test that weekdays are business days."""
        config = BusinessRulesConfig()
        assert config.is_business_day(0) is True  # Monday
        assert config.is_business_day(1) is True  # Tuesday
        assert config.is_business_day(2) is True  # Wednesday
        assert config.is_business_day(3) is True  # Thursday
        assert config.is_business_day(4) is True  # Friday

    def test_is_business_day_weekends(self) -> None:
        """Test that weekends are not business days."""
        config = BusinessRulesConfig()
        assert config.is_business_day(5) is False  # Saturday
        assert config.is_business_day(6) is False  # Sunday


class TestBusinessRulesEnvironment:
    """Test environment variable handling."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        BusinessRulesConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        BusinessRulesConfig.reset()

    @patch.dict(os.environ, {"STOCKBOOK_MAX_POSITIONS": "20"})
    def test_max_positions_from_env(self) -> None:
        """Test loading max positions from environment."""
        config = BusinessRulesConfig()
        assert config.portfolio_defaults["max_positions"] == 20

    @patch.dict(os.environ, {"STOCKBOOK_MAX_RISK_PER_TRADE": "5.0"})
    def test_max_risk_per_trade_from_env(self) -> None:
        """Test loading max risk per trade from environment."""
        config = BusinessRulesConfig()
        assert config.portfolio_defaults["max_risk_per_trade"] == 5.0

    @patch.dict(os.environ, {"STOCKBOOK_PORTFOLIO_PREFIX": "MyPortfolio"})
    def test_portfolio_prefix_from_env(self) -> None:
        """Test loading portfolio prefix from environment."""
        config = BusinessRulesConfig()
        assert config.portfolio_defaults["name_prefix"] == "MyPortfolio"

    @patch.dict(
        os.environ,
        {
            "STOCKBOOK_MAX_POSITIONS": "15",
            "STOCKBOOK_MAX_RISK_PER_TRADE": "3.5",
            "STOCKBOOK_PORTFOLIO_PREFIX": "CustomPortfolio",
        },
    )
    def test_all_portfolio_defaults_from_env(self) -> None:
        """Test loading all portfolio defaults from environment."""
        config = BusinessRulesConfig()
        assert config.portfolio_defaults["max_positions"] == 15
        assert config.portfolio_defaults["max_risk_per_trade"] == 3.5
        assert config.portfolio_defaults["name_prefix"] == "CustomPortfolio"


class TestBusinessRulesValidation:
    """Test business rules validation."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        BusinessRulesConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        BusinessRulesConfig.reset()

    def test_validate_passes_with_defaults(self) -> None:
        """Test that validation passes with default values."""
        _ = BusinessRulesConfig()
        # Should not raise during initialization

    @patch.dict(os.environ, {"STOCKBOOK_MAX_POSITIONS": "0"})
    def test_validate_fails_max_positions_zero(self) -> None:
        """Test validation fails when max_positions is zero."""
        with pytest.raises(ValidationError, match="max_positions must be positive"):
            _ = BusinessRulesConfig()

    @patch.dict(os.environ, {"STOCKBOOK_MAX_POSITIONS": "-5"})
    def test_validate_fails_max_positions_negative(self) -> None:
        """Test validation fails when max_positions is negative."""
        with pytest.raises(ValidationError, match="max_positions must be positive"):
            _ = BusinessRulesConfig()

    @patch.dict(os.environ, {"STOCKBOOK_MAX_RISK_PER_TRADE": "0"})
    def test_validate_fails_max_risk_zero(self) -> None:
        """Test validation fails when max_risk_per_trade is zero."""
        with pytest.raises(
            ValidationError,
            match="max_risk_per_trade must be positive",
        ):
            _ = BusinessRulesConfig()

    @patch.dict(os.environ, {"STOCKBOOK_MAX_RISK_PER_TRADE": "-1.5"})
    def test_validate_fails_max_risk_negative(self) -> None:
        """Test validation fails when max_risk_per_trade is negative."""
        with pytest.raises(
            ValidationError,
            match="max_risk_per_trade must be positive",
        ):
            _ = BusinessRulesConfig()

    def test_inheritance_from_base_config(self) -> None:
        """Test that BusinessRulesConfig inherits BaseConfig methods."""
        config = BusinessRulesConfig()

        # Should have access to BaseConfig static methods
        assert hasattr(config, "get_env_str")
        assert hasattr(config, "get_env_int")
        assert hasattr(config, "get_env_float")
        assert hasattr(config, "get_env_bool")
        assert hasattr(config, "get_env_list")


class TestBusinessRulesMethods:
    """Test BusinessRulesConfig methods."""

    def setup_method(self) -> None:
        """Ensure clean state."""
        BusinessRulesConfig.reset()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        BusinessRulesConfig.reset()

    def test_is_business_day_with_valid_days(self) -> None:
        """Test is_business_day with valid day values."""
        config = BusinessRulesConfig()

        # Test all valid weekday values
        for day in range(7):
            if day < 5:  # Monday-Friday
                assert config.is_business_day(day) is True
            else:  # Saturday-Sunday
                assert config.is_business_day(day) is False

    def test_is_business_day_with_invalid_days(self) -> None:
        """Test is_business_day with invalid day values."""
        config = BusinessRulesConfig()

        # Test invalid day values
        assert config.is_business_day(-1) is False
        assert config.is_business_day(7) is False
        assert config.is_business_day(100) is False
