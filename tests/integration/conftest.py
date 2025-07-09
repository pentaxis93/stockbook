"""Pytest configuration for integration tests."""

import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Configure anyio to only use asyncio backend, not trio."""
    return "asyncio"
