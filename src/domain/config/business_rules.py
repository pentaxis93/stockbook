"""Configuration for domain business rules."""

from src.shared.config.base import BaseConfig, ValidationError


class BusinessRulesConfig(BaseConfig):
    """Configuration for domain business rules."""

    _instance = None
    _initialized = False

    def __new__(cls) -> "BusinessRulesConfig":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize business rules configuration."""
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
        self._setup_portfolio_defaults()
        self._setup_business_days()
        self._validate_values()

    def _setup_portfolio_defaults(self) -> None:
        """Setup default portfolio configuration."""
        self.portfolio_defaults = {
            "max_positions": self.get_env_int("STOCKBOOK_MAX_POSITIONS", 10),
            "max_risk_per_trade": self.get_env_float(
                "STOCKBOOK_MAX_RISK_PER_TRADE",
                2.0,
            ),
            "name_prefix": self.get_env_str("STOCKBOOK_PORTFOLIO_PREFIX", "Portfolio"),
        }

    def _setup_business_days(self) -> None:
        """Setup business day configuration."""
        self.business_days = {0, 1, 2, 3, 4}  # Monday through Friday
        self.market_holidays: list[str] = []  # Can be populated from external source

    def _validate_values(self) -> None:
        """Validate business rule values."""
        max_positions = self.portfolio_defaults.get("max_positions", 0)
        if isinstance(max_positions, int) and max_positions <= 0:
            msg = "max_positions must be positive"
            raise ValidationError(msg)

        max_risk = self.portfolio_defaults.get("max_risk_per_trade", 0.0)
        if isinstance(max_risk, float) and max_risk <= 0:
            msg = "max_risk_per_trade must be positive"
            raise ValidationError(msg)

    def is_business_day(self, weekday: int) -> bool:
        """Check if a weekday is a business day."""
        return weekday in self.business_days


# Global business rules config instance
business_rules_config = BusinessRulesConfig()
