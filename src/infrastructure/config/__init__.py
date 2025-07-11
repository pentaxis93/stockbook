"""Infrastructure configuration module.

Contains database and file system configuration for the infrastructure layer.
"""

from src.infrastructure.config.database_config import DatabaseConfig, database_config
from src.infrastructure.config.paths_config import PathsConfig, paths_config

__all__ = [
    "DatabaseConfig",
    "PathsConfig",
    "database_config",
    "paths_config",
]
