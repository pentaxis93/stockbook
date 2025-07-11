"""Setup configuration for stockbook package."""

from setuptools import find_packages, setup

# Import version from the version module
from src.version import __version__

# Only run setup() when this file is executed directly, not when imported.
# This allows the file to be safely imported by test runners and coverage tools.
if __name__ == "__main__":
    setup(
        name="stockbook",
        version=__version__,
        packages=find_packages(),
        python_requires=">=3.12",
        install_requires=[],  # Dependencies are managed in requirements.txt
    )
