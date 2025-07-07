"""
Test suite for setup.py configuration.

Tests the package setup configuration to ensure proper metadata
and dependencies are defined.
"""

import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch


class TestSetupConfiguration:
    """Test the setup.py configuration."""

    def test_setup_file_exists(self) -> None:
        """Test that setup.py exists in the project root."""
        setup_path = Path("setup.py")
        assert setup_path.exists()
        assert setup_path.is_file()

    def test_setup_imports_required_modules(self) -> None:
        """Test that setup.py imports required setuptools modules."""
        setup_path = Path("setup.py")
        content = setup_path.read_text(encoding="utf-8")

        assert "from setuptools import find_packages, setup" in content
        assert "setup(" in content

    def test_setup_has_main_guard(self) -> None:
        """Test that setup.py has proper if __name__ == '__main__' guard."""
        setup_path = Path("setup.py")
        content = setup_path.read_text(encoding="utf-8")

        assert 'if __name__ == "__main__":' in content
        # Ensure setup() is inside the guard
        lines = content.split("\n")
        main_guard_index = next(
            i for i, line in enumerate(lines) if 'if __name__ == "__main__":' in line
        )
        setup_call_indices = [
            i
            for i, line in enumerate(lines)
            if "setup(" in line and not line.strip().startswith("from")
        ]
        # There should be a setup() call after the main guard
        assert any(idx > main_guard_index for idx in setup_call_indices)

    def test_setup_can_be_imported(self) -> None:
        """Test that setup.py can be safely imported without execution."""
        # This should not raise any errors or execute setup()
        import setup

        # Verify the module was imported
        assert hasattr(setup, "__file__")
        # Clean up
        del setup

    def test_setup_defines_package_metadata(self) -> None:
        """Test that setup.py defines required package metadata."""
        setup_path = Path("setup.py")
        content = setup_path.read_text(encoding="utf-8")

        # Check for required metadata fields
        assert 'name="stockbook"' in content
        assert "version=" in content
        assert "packages=find_packages()" in content
        assert "python_requires=" in content

    def test_setup_python_version_requirement(self) -> None:
        """Test that setup.py specifies Python version requirement."""
        setup_path = Path("setup.py")
        content = setup_path.read_text(encoding="utf-8")

        # Should require Python 3.13 or higher based on the file content
        assert 'python_requires=">=3.13"' in content

    @patch("setuptools.setup")
    @patch("setuptools.find_packages")
    def test_setup_function_arguments(
        self,
        mock_find_packages: Mock,
        mock_setup: Mock,
    ) -> None:
        """Test that setup() is called with correct arguments when executed."""
        # Mock find_packages to return expected value
        mock_find_packages.return_value = ["src", "src.domain", "src.application"]

        # Execute setup.py as a script
        setup_path = Path("setup.py")
        setup_code = setup_path.read_text(encoding="utf-8")
        exec(  # noqa: S102
            compile(setup_code, "setup.py", "exec"),
            {"__name__": "__main__"},
        )

        # Verify setup was called
        mock_setup.assert_called_once()

        # Get the arguments passed to setup()
        call_args = mock_setup.call_args[1]

        # Verify required arguments
        assert call_args["name"] == "stockbook"
        assert call_args["version"] == "0.1.0"
        assert call_args["packages"] == ["src", "src.domain", "src.application"]
        assert call_args["python_requires"] == ">=3.13"
        assert "install_requires" in call_args

    def test_setup_executable(self) -> None:
        """Test that setup.py can be executed without errors."""
        # Run setup.py with --help to avoid actually installing
        result = subprocess.run(  # noqa: S603
            [sys.executable, "setup.py", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Should exit successfully
        assert result.returncode == 0
        # Should show help text
        assert "usage:" in result.stdout.lower()

    def test_setup_version_format(self) -> None:
        """Test that the version number follows semantic versioning."""
        setup_path = Path("setup.py")
        content = setup_path.read_text(encoding="utf-8")

        # Extract version
        version_match = re.search(r'version="([^"]+)"', content)
        assert version_match is not None

        version = version_match.group(1)
        # Check semantic versioning format (X.Y.Z)
        assert re.match(r"^\d+\.\d+\.\d+$", version) is not None

    def test_setup_install_requires_format(self) -> None:
        """Test that install_requires is properly formatted."""
        setup_path = Path("setup.py")
        content = setup_path.read_text(encoding="utf-8")

        # Check that install_requires is defined as a list
        assert "install_requires=[]" in content or "install_requires=[" in content

        # Check comment about requirements.txt
        assert "requirements.txt" in content
