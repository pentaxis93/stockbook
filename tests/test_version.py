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

    def test_version_is_current(self) -> None:
        """Test that version is properly set and matches expected format."""
        from src.version import __version__, __version_info__

        # Version should match the version_info tuple
        version_from_tuple = ".".join(str(part) for part in __version_info__)
        assert __version__ == version_from_tuple

        # Version should be semantic versioning compliant
        pattern = r"^\d+\.\d+\.\d+$"
        assert re.match(pattern, __version__) is not None

    def test_version_info_tuple(self) -> None:
        """Test that version info tuple is properly formatted."""
        from src.version import __version_info__

        assert isinstance(__version_info__, tuple)
        assert len(__version_info__) == 3
        assert all(isinstance(part, int) for part in __version_info__)
        # Don't hardcode the version numbers
        assert all(part >= 0 for part in __version_info__)

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
            assert isinstance(version.VERSION_MAJOR, int)
            assert version.VERSION_MAJOR >= 0
            assert version.__version_info__[0] == version.VERSION_MAJOR
        if hasattr(version, "VERSION_MINOR"):
            assert isinstance(version.VERSION_MINOR, int)
            assert version.VERSION_MINOR >= 0
            assert version.__version_info__[1] == version.VERSION_MINOR
        if hasattr(version, "VERSION_PATCH"):
            assert isinstance(version.VERSION_PATCH, int)
            assert version.VERSION_PATCH >= 0
            assert version.__version_info__[2] == version.VERSION_PATCH

    def test_version_string_generation(self) -> None:
        """Test version string generation function if it exists."""
        from src import version

        if hasattr(version, "get_version"):
            ver = version.get_version()
            assert isinstance(ver, str)
            assert re.match(r"^\d+\.\d+\.\d+$", ver)
            assert ver == version.__version__

        if hasattr(version, "get_full_version"):
            full_version = version.get_full_version()
            assert "StockBook" in full_version
            assert version.__version__ in full_version

    def test_get_version_function(self) -> None:
        """Test the get_version function returns correct version."""
        from src.version import __version__, get_version

        result = get_version()
        assert result == __version__
        assert isinstance(result, str)
        assert re.match(r"^\d+\.\d+\.\d+$", result)

    def test_get_full_version_function(self) -> None:
        """Test the get_full_version function returns properly formatted string."""
        from src.version import __release_date__, __version__, get_full_version

        full_version = get_full_version()
        # Check the format without hardcoding version
        expected_format = f"StockBook {__version__} (Released: {__release_date__})"
        assert full_version == expected_format
        assert "StockBook" in full_version
        assert __version__ in full_version
        assert "Released:" in full_version
        assert __release_date__ in full_version

    def test_version_import_from_src(self) -> None:
        """Test that version can be imported from src package."""
        from src import __version__
        from src.version import __version__ as version_module_version

        # Should be able to import version from src package
        assert isinstance(__version__, str)
        assert re.match(r"^\d+\.\d+\.\d+$", __version__)
        # Should match the version in the version module
        assert __version__ == version_module_version

    def test_version_module_docstring(self) -> None:
        """Test that version module has proper documentation."""
        from src import version

        assert version.__doc__ is not None
        assert len(version.__doc__.strip()) > 0
