"""Domain configuration module.

Contains validation rules and business rules that govern domain behavior.
"""

from src.domain.config.business_rules import BusinessRulesConfig, business_rules
from src.domain.config.validation_rules import ValidationRulesConfig, validation_rules

__all__ = [
    "BusinessRulesConfig",
    "ValidationRulesConfig",
    "business_rules",
    "validation_rules",
]
