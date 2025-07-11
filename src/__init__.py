"""StockBook Application - A comprehensive stock portfolio management system.

This package implements a clean architecture with four distinct layers:
- Domain: Core business logic and entities
- Application: Use cases and application services
- Infrastructure: External concerns (database, file system)
- Presentation: User interface and controllers

The architecture enforces proper dependency directions and maintains
separation of concerns across all layers.
"""

from src.version import __api_version__, __release_date__, __version__, __version_info__

__all__ = ["__api_version__", "__release_date__", "__version__", "__version_info__"]
