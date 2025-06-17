"""
Dependency lifetime management enumerations.

Defines how long instances should live and when they should be created.
"""

from enum import Enum


class Lifetime(Enum):
    """Defines the lifetime of a registered service."""

    SINGLETON = "singleton"
    """Single instance shared across all resolutions."""

    TRANSIENT = "transient"
    """New instance created for each resolution."""

    SCOPED = "scoped"
    """Single instance per scope (future enhancement)."""
