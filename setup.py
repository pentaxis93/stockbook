"""Setup configuration for stockbook package."""

from setuptools import find_packages, setup

setup(
    name="stockbook",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.13",
    install_requires=[],  # Dependencies are managed in requirements.txt
)
