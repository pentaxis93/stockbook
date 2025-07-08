"""Setup configuration for stockbook package."""

from setuptools import find_packages, setup

# Only run setup() when this file is executed directly, not when imported.
# This allows the file to be safely imported by test runners and coverage tools.
if __name__ == "__main__":
    setup(
        name="stockbook",
        version="0.1.0",
        packages=find_packages(),
        python_requires=">=3.12",
        install_requires=[],  # Dependencies are managed in requirements.txt
    )
