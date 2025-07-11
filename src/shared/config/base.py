"""Base configuration class with common utilities."""

import os


class ConfigError(Exception):
    """Base exception for configuration errors."""


class ValidationError(ConfigError):
    """Exception raised when configuration validation fails."""


class BaseConfig:
    """Base configuration class with common utility methods."""

    @staticmethod
    def get_env_str(key: str, default: str) -> str:
        """Get string value from environment with default."""
        return os.getenv(key, default)

    @staticmethod
    def get_env_int(key: str, default: int) -> int:
        """Get integer value from environment with default."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError as exc:
            msg = f"Invalid integer value for {key}: {value}"
            raise ConfigError(msg) from exc

    @staticmethod
    def get_env_float(key: str, default: float) -> float:
        """Get float value from environment with default."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError as exc:
            msg = f"Invalid float value for {key}: {value}"
            raise ConfigError(msg) from exc

    @staticmethod
    def get_env_bool(key: str, *, default: bool) -> bool:
        """Get boolean value from environment with default."""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    @staticmethod
    def get_env_list(key: str, default: list[str]) -> list[str]:
        """Get list value from environment with default."""
        value = os.getenv(key)
        if value is None:
            return default
        return [item.strip() for item in value.split(",")]
