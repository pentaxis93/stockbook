"""Shared fixtures for table tests."""

import tempfile
from typing import Generator

import pytest
import sqlalchemy as sa
from sqlalchemy.engine import Engine


@pytest.fixture
def temp_database() -> Generator[Engine, None, None]:
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        engine = sa.create_engine(f"sqlite:///{tmp.name}")
        yield engine
        engine.dispose()
