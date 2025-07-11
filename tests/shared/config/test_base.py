"""Tests for base configuration utilities."""

import os
from unittest.mock import patch

import pytest

from src.shared.config.base import BaseConfig, ConfigError, ValidationError


class TestConfigExceptions:
    """Test configuration exception classes."""

    def test_config_error_inheritance(self) -> None:
        """Test that ConfigError is an Exception."""
        assert issubclass(ConfigError, Exception)

    def test_validation_error_inheritance(self) -> None:
        """Test that ValidationError inherits from ConfigError."""
        assert issubclass(ValidationError, ConfigError)
        assert issubclass(ValidationError, Exception)

    def test_config_error_instantiation(self) -> None:
        """Test ConfigError can be instantiated with message."""
        error = ConfigError("Test error message")
        assert str(error) == "Test error message"

    def test_validation_error_instantiation(self) -> None:
        """Test ValidationError can be instantiated with message."""
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"


class TestBaseConfig:
    """Test BaseConfig utility methods."""

    def setup_method(self) -> None:
        """Setup test instance."""
        self.config = BaseConfig()

    def test_base_config_instantiation(self) -> None:
        """Test BaseConfig can be instantiated."""
        assert isinstance(self.config, BaseConfig)

    @patch.dict(os.environ, {"TEST_STRING": "test_value"})
    def test_get_env_str_with_env_var(self) -> None:
        """Test getting string from environment variable."""
        result = BaseConfig.get_env_str("TEST_STRING", "default")
        assert result == "test_value"

    def test_get_env_str_with_default(self) -> None:
        """Test getting string with default when env var missing."""
        result = BaseConfig.get_env_str("NONEXISTENT_VAR", "default_value")
        assert result == "default_value"

    @patch.dict(os.environ, {"TEST_INT": "42"})
    def test_get_env_int_with_env_var(self) -> None:
        """Test getting integer from environment variable."""
        result = BaseConfig.get_env_int("TEST_INT", 0)
        assert result == 42

    def test_get_env_int_with_default(self) -> None:
        """Test getting integer with default when env var missing."""
        result = BaseConfig.get_env_int("NONEXISTENT_VAR", 99)
        assert result == 99

    @patch.dict(os.environ, {"TEST_INT": "not_a_number"})
    def test_get_env_int_with_invalid_value(self) -> None:
        """Test getting integer raises error for invalid value."""
        with pytest.raises(
            ConfigError,
            match="Invalid integer value for TEST_INT: not_a_number",
        ):
            _ = BaseConfig.get_env_int("TEST_INT", 0)

    @patch.dict(os.environ, {"TEST_FLOAT": "3.14"})
    def test_get_env_float_with_env_var(self) -> None:
        """Test getting float from environment variable."""
        result = BaseConfig.get_env_float("TEST_FLOAT", 0.0)
        assert result == 3.14

    def test_get_env_float_with_default(self) -> None:
        """Test getting float with default when env var missing."""
        result = BaseConfig.get_env_float("NONEXISTENT_VAR", 2.718)
        assert result == 2.718

    @patch.dict(os.environ, {"TEST_FLOAT": "not_a_float"})
    def test_get_env_float_with_invalid_value(self) -> None:
        """Test getting float raises error for invalid value."""
        with pytest.raises(
            ConfigError,
            match="Invalid float value for TEST_FLOAT: not_a_float",
        ):
            _ = BaseConfig.get_env_float("TEST_FLOAT", 0.0)

    @patch.dict(os.environ, {"TEST_BOOL_TRUE": "true"})
    def test_get_env_bool_true_lowercase(self) -> None:
        """Test getting boolean true from 'true'."""
        result = BaseConfig.get_env_bool("TEST_BOOL_TRUE", default=False)
        assert result is True

    @patch.dict(os.environ, {"TEST_BOOL_TRUE": "TRUE"})
    def test_get_env_bool_true_uppercase(self) -> None:
        """Test getting boolean true from 'TRUE'."""
        result = BaseConfig.get_env_bool("TEST_BOOL_TRUE", default=False)
        assert result is True

    @patch.dict(os.environ, {"TEST_BOOL_TRUE": "1"})
    def test_get_env_bool_true_numeric(self) -> None:
        """Test getting boolean true from '1'."""
        result = BaseConfig.get_env_bool("TEST_BOOL_TRUE", default=False)
        assert result is True

    @patch.dict(os.environ, {"TEST_BOOL_TRUE": "yes"})
    def test_get_env_bool_true_yes(self) -> None:
        """Test getting boolean true from 'yes'."""
        result = BaseConfig.get_env_bool("TEST_BOOL_TRUE", default=False)
        assert result is True

    @patch.dict(os.environ, {"TEST_BOOL_TRUE": "on"})
    def test_get_env_bool_true_on(self) -> None:
        """Test getting boolean true from 'on'."""
        result = BaseConfig.get_env_bool("TEST_BOOL_TRUE", default=False)
        assert result is True

    @patch.dict(os.environ, {"TEST_BOOL_FALSE": "false"})
    def test_get_env_bool_false(self) -> None:
        """Test getting boolean false from 'false'."""
        result = BaseConfig.get_env_bool("TEST_BOOL_FALSE", default=True)
        assert result is False

    @patch.dict(os.environ, {"TEST_BOOL_FALSE": "0"})
    def test_get_env_bool_false_numeric(self) -> None:
        """Test getting boolean false from '0'."""
        result = BaseConfig.get_env_bool("TEST_BOOL_FALSE", default=True)
        assert result is False

    @patch.dict(os.environ, {"TEST_BOOL_FALSE": "no"})
    def test_get_env_bool_false_no(self) -> None:
        """Test getting boolean false from 'no'."""
        result = BaseConfig.get_env_bool("TEST_BOOL_FALSE", default=True)
        assert result is False

    def test_get_env_bool_with_default(self) -> None:
        """Test getting boolean with default when env var missing."""
        result = BaseConfig.get_env_bool("NONEXISTENT_VAR", default=True)
        assert result is True

    @patch.dict(os.environ, {"TEST_LIST": "item1,item2,item3"})
    def test_get_env_list_with_env_var(self) -> None:
        """Test getting list from comma-separated environment variable."""
        result = BaseConfig.get_env_list("TEST_LIST", [])
        assert result == ["item1", "item2", "item3"]

    @patch.dict(os.environ, {"TEST_LIST": "item1, item2 , item3"})
    def test_get_env_list_with_spaces(self) -> None:
        """Test getting list handles spaces correctly."""
        result = BaseConfig.get_env_list("TEST_LIST", [])
        assert result == ["item1", "item2", "item3"]

    @patch.dict(os.environ, {"TEST_LIST": "single_item"})
    def test_get_env_list_single_item(self) -> None:
        """Test getting list with single item."""
        result = BaseConfig.get_env_list("TEST_LIST", [])
        assert result == ["single_item"]

    @patch.dict(os.environ, {"TEST_LIST": ""})
    def test_get_env_list_empty_string(self) -> None:
        """Test getting list from empty string."""
        result = BaseConfig.get_env_list("TEST_LIST", ["default"])
        assert result == [""]

    def test_get_env_list_with_default(self) -> None:
        """Test getting list with default when env var missing."""
        result = BaseConfig.get_env_list("NONEXISTENT_VAR", ["default1", "default2"])
        assert result == ["default1", "default2"]

    def test_all_methods_are_static(self) -> None:
        """Test that all utility methods can be called statically."""
        # Test that methods can be called without instance
        assert BaseConfig.get_env_str("NONEXISTENT", "default") == "default"
        assert BaseConfig.get_env_int("NONEXISTENT", 42) == 42
        assert BaseConfig.get_env_float("NONEXISTENT", 3.14) == 3.14
        assert BaseConfig.get_env_bool("NONEXISTENT", default=True) is True
        assert BaseConfig.get_env_list("NONEXISTENT", ["a", "b"]) == ["a", "b"]
