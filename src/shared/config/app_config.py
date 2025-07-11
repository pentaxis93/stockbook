"""Application-wide configuration.

This module contains cross-cutting configuration that doesn't belong
to any specific layer, including application metadata and feature flags.
"""

from src.shared.config.base import BaseConfig


class AppConfig(BaseConfig):
    """Application-wide configuration settings."""

    _instance = None
    _initialized = False

    def __new__(cls) -> "AppConfig":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize application configuration."""
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
        self._setup_application_settings()
        self._setup_feature_flags()

    def _setup_application_settings(self) -> None:
        """Setup application settings."""
        self.app_name = self.get_env_str("STOCKBOOK_APP_NAME", "StockBook")
        self.DEBUG = self.get_env_bool("STOCKBOOK_DEBUG", default=False)

        # Import version information
        from src.version import __api_version__, __release_date__, __version__

        self.app_version = __version__
        self.app_release_date = __release_date__
        self.api_version = __api_version__

    def _setup_feature_flags(self) -> None:
        """Setup feature flags for different development phases."""
        self.features = {
            # Core features (Phase 1-2)
            "stock_management": self.get_env_bool(
                "STOCKBOOK_FEATURE_STOCKS",
                default=True,
            ),
            "portfolio_management": self.get_env_bool(
                "STOCKBOOK_FEATURE_PORTFOLIOS",
                default=True,
            ),
            "transaction_recording": self.get_env_bool(
                "STOCKBOOK_FEATURE_TRANSACTIONS",
                default=True,
            ),
            # Advanced features (Phase 3)
            "target_management": self.get_env_bool(
                "STOCKBOOK_FEATURE_TARGETS",
                default=False,
            ),
            "journal_system": self.get_env_bool(
                "STOCKBOOK_FEATURE_JOURNAL",
                default=False,
            ),
            "analytics": self.get_env_bool(
                "STOCKBOOK_FEATURE_ANALYTICS",
                default=False,
            ),
            # Future features (Phase 4)
            "multi_account": self.get_env_bool(
                "STOCKBOOK_FEATURE_MULTI_ACCOUNT",
                default=False,
            ),
            "api_integration": self.get_env_bool(
                "STOCKBOOK_FEATURE_API",
                default=False,
            ),
        }

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        return self.features.get(feature_name, False)

    def get_version_info(self) -> dict[str, str]:
        """Get application version information.

        Returns:
            Dict containing version, release date, and API version.
        """
        return {
            "version": self.app_version,
            "release_date": self.app_release_date,
            "api_version": self.api_version,
        }


# Global app config instance
app_config = AppConfig()
