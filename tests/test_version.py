"""
Test suite for version module.

Tests the centralized version management system to ensure proper
version formatting, metadata, and accessibility.
"""

import datetime
import re

import pytest


class TestVersionModule:
    """Test the version module functionality."""

    def test_version_module_exists(self) -> None:
        """Test that version module exists and can be imported."""
        from src import version

        assert hasattr(version, "__version__")

    def test_version_string_format(self) -> None:
        """Test that version string follows semantic versioning."""
        from src.version import __version__

        # Should match semantic versioning pattern X.Y.Z
        pattern = r"^\d+\.\d+\.\d+$"
        assert re.match(pattern, __version__) is not None

    def test_version_is_0_2_1(self) -> None:
        """Test that current version is 0.2.1 as specified."""
        from src.version import __version__

        assert __version__ == "0.2.1"

    def test_version_info_tuple(self) -> None:
        """Test that version info tuple is properly formatted."""
        from src.version import __version_info__

        assert isinstance(__version_info__, tuple)
        assert len(__version_info__) == 3
        assert all(isinstance(part, int) for part in __version_info__)
        assert __version_info__ == (0, 2, 1)

    def test_version_string_matches_tuple(self) -> None:
        """Test that version string matches version info tuple."""
        from src.version import __version__, __version_info__

        version_from_tuple = ".".join(str(part) for part in __version_info__)
        assert __version__ == version_from_tuple

    def test_release_date_exists(self) -> None:
        """Test that release date is defined and properly formatted."""
        from src.version import __release_date__

        assert isinstance(__release_date__, str)
        # Should be in YYYY-MM-DD format
        try:
            year, month, day = __release_date__.split("-")
            _ = datetime.date(int(year), int(month), int(day))
        except (ValueError, AttributeError):
            pytest.fail("Release date is not in YYYY-MM-DD format")

    def test_api_version_exists(self) -> None:
        """Test that API version is defined."""
        from src.version import __api_version__

        assert isinstance(__api_version__, str)
        assert __api_version__ == "v1"

    def test_version_metadata_attributes(self) -> None:
        """Test that all expected version metadata attributes exist."""
        from src import version

        expected_attributes = [
            "__version__",
            "__version_info__",
            "__release_date__",
            "__api_version__",
        ]

        for attr in expected_attributes:
            assert hasattr(version, attr)

    def test_version_module_all_exports(self) -> None:
        """Test that __all__ properly exports version attributes."""
        from src import version

        if hasattr(version, "__all__"):
            # If __all__ is defined, check it includes version attributes
            assert "__version__" in version.__all__
            assert "__version_info__" in version.__all__
            assert "__release_date__" in version.__all__
            assert "__api_version__" in version.__all__

    def test_version_comparison_helpers(self) -> None:
        """Test version comparison helper functions if they exist."""
        from src import version

        # Test major, minor, patch properties if they exist
        if hasattr(version, "VERSION_MAJOR"):
            assert version.VERSION_MAJOR == 0
        if hasattr(version, "VERSION_MINOR"):
            assert version.VERSION_MINOR == 2
        if hasattr(version, "VERSION_PATCH"):
            assert version.VERSION_PATCH == 1

    def test_version_string_generation(self) -> None:
        """Test version string generation function if it exists."""
        from src import version

        if hasattr(version, "get_version"):
            assert version.get_version() == "0.2.1"

        if hasattr(version, "get_full_version"):
            full_version = version.get_full_version()
            assert "0.2.1" in full_version

    def test_get_version_function(self) -> None:
        """Test the get_version function returns correct version."""
        from src.version import get_version

        assert get_version() == "0.2.1"

    def test_get_full_version_function(self) -> None:
        """Test the get_full_version function returns properly formatted string."""
        from src.version import get_full_version

        full_version = get_full_version()
        assert full_version == "StockBook 0.2.1 (Released: 2025-01-11)"
        assert "StockBook" in full_version
        assert "0.2.1" in full_version
        assert "Released: 2025-01-11" in full_version

    def test_version_import_from_src(self) -> None:
        """Test that version can be imported from src package."""
        from src import __version__

        assert __version__ == "0.2.1"

    def test_version_module_docstring(self) -> None:
        """Test that version module has proper documentation."""
        from src import version

        assert version.__doc__ is not None
        assert len(version.__doc__.strip()) > 0
