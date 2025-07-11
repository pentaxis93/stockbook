"""Version information for StockBook.

This module provides centralized version management for the StockBook application.
It defines the version number, release date, and other metadata following
semantic versioning principles.

The version should be updated here whenever a new release is made.
All other parts of the application should import version information from this module.

Attributes:
    __version__ (str): The current version string in semantic versioning format (X.Y.Z).
    __version_info__ (tuple): Version components as a tuple (major, minor, patch).
    __release_date__ (str): The release date in YYYY-MM-DD format.
    __api_version__ (str): The API version identifier.
"""

__version__ = "0.4.2"
__version_info__ = (0, 4, 2)
__release_date__ = "2025-01-11"
__api_version__ = "v1"

# Version components for easy access
VERSION_MAJOR = __version_info__[0]
VERSION_MINOR = __version_info__[1]
VERSION_PATCH = __version_info__[2]

# Export all version attributes
__all__ = [
    "VERSION_MAJOR",
    "VERSION_MINOR",
    "VERSION_PATCH",
    "__api_version__",
    "__release_date__",
    "__version__",
    "__version_info__",
    "get_full_version",
    "get_version",
]


def get_version() -> str:
    """Get the version string.

    Returns:
        str: The version string in X.Y.Z format.
    """
    return __version__


def get_full_version() -> str:
    """Get the full version string with metadata.

    Returns:
        str: Full version string including version and release date.
    """
    return f"StockBook {__version__} (Released: {__release_date__})"
