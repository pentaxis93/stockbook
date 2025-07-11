"""Database engine factory for SQLAlchemy.

This module provides factory functions for creating SQLAlchemy engines
with appropriate configuration based on the database URL.
"""

# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

from typing import Any
from urllib.parse import urlparse

from sqlalchemy import create_engine as sqla_create_engine
from sqlalchemy.engine import Engine

from src.infrastructure.config import database_config
from src.infrastructure.persistence.dialects.sqlite import (
    configure_sqlite_engine,
    get_sqlite_engine_kwargs,
)
from src.shared.config import app_config


def create_engine(
    database_url: str,
    *,
    echo: bool = False,
    **kwargs: Any,
) -> Engine:
    """Create a SQLAlchemy engine based on database URL.

    Args:
        database_url: Database URL (e.g., "sqlite:///path/to/db.db")
        echo: Whether to log SQL statements
        **kwargs: Additional arguments passed to create_engine

    Returns:
        Configured SQLAlchemy engine

    Raises:
        ValueError: If database_url is empty or unsupported
    """
    if not database_url:
        msg = "Database URL cannot be empty"
        raise ValueError(msg)

    # Parse the URL to determine database type
    parsed = urlparse(database_url)
    scheme = parsed.scheme

    # Get dialect-specific configuration
    if scheme == "sqlite":
        dialect_kwargs = get_sqlite_engine_kwargs(database_url)
        kwargs.update(dialect_kwargs)
    else:
        msg = f"Unsupported database scheme: {scheme}"
        raise ValueError(msg)

    # Create engine
    engine = sqla_create_engine(
        database_url,
        echo=echo,
        **kwargs,
    )

    # Apply dialect-specific configuration
    if scheme == "sqlite":
        configure_sqlite_engine(engine)

    return engine


def create_engine_from_config(*, use_test_db: bool = False) -> Engine:
    """Create a SQLAlchemy engine using application configuration.

    Args:
        use_test_db: Whether to use test database URL

    Returns:
        Configured SQLAlchemy engine
    """
    database_url = database_config.get_connection_string(test=use_test_db)

    return create_engine(
        database_url,
        echo=app_config.DEBUG,
    )
