"""
Database engine factory for SQLAlchemy.

This module provides factory functions for creating SQLAlchemy engines
with appropriate configuration for SQLite databases.
"""

from pathlib import Path
from typing import Any, Optional, Union

from sqlalchemy import create_engine as sqla_create_engine
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from config import Config


def create_engine(
    db_path: Union[str, Path],
    echo: bool = False,
    **kwargs: Any,
) -> Engine:
    """
    Create a SQLAlchemy engine for SQLite database.

    Args:
        db_path: Path to the database file or ":memory:" for in-memory
        echo: Whether to log SQL statements
        **kwargs: Additional arguments passed to create_engine

    Returns:
        Configured SQLAlchemy engine

    Raises:
        TypeError: If db_path is not a string or Path
        ValueError: If db_path is empty
    """
    # Validate input
    if not isinstance(
        db_path, (str, Path)
    ):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise TypeError("Database path must be a string or Path object")

    db_path_str = str(db_path)
    if not db_path_str:
        raise ValueError("Database path cannot be empty")

    # Build database URL
    url = get_database_url(db_path_str)

    # Configure connection arguments
    connect_args = {"check_same_thread": False}

    # Special configuration for in-memory databases
    if db_path_str == ":memory:":
        # Use StaticPool for in-memory databases to share connection
        kwargs["poolclass"] = StaticPool

    # Create engine
    engine = sqla_create_engine(
        url,
        echo=echo,
        connect_args=connect_args,
        **kwargs,
    )

    # Configure SQLite pragmas
    @event.listens_for(engine, "connect")  # type: ignore[misc,no-untyped-call]
    def set_sqlite_pragma(dbapi_conn: Any, connection_record: Any) -> None:
        """Configure SQLite pragmas on each connection."""
        configure_sqlite_pragmas(dbapi_conn, enable_foreign_keys=True)

    # Mark function as used by SQLAlchemy event system
    _ = set_sqlite_pragma

    return engine


def create_engine_from_config(use_test_db: bool = False) -> Engine:
    """
    Create a SQLAlchemy engine using application configuration.

    Args:
        use_test_db: Whether to use test database path

    Returns:
        Configured SQLAlchemy engine
    """
    config = Config()
    db_path = config.test_db_path if use_test_db else config.db_path

    # The timeout will be passed as part of the connect_args in create_engine
    return create_engine(
        db_path,
        echo=config.DEBUG,
    )


def get_database_url(db_path: Union[str, Path]) -> str:
    """
    Construct SQLite database URL from path.

    Args:
        db_path: Database file path

    Returns:
        SQLite URL string
    """
    return f"sqlite:///{db_path}"


def configure_sqlite_pragmas(
    connection: Any,
    enable_foreign_keys: bool = True,
    journal_mode: Optional[str] = None,
) -> None:
    """
    Configure SQLite PRAGMA settings on a connection.

    Args:
        connection: SQLite database connection
        enable_foreign_keys: Whether to enable foreign key constraints
        journal_mode: Journal mode (e.g., "WAL", "DELETE")
    """
    cursor = connection.cursor()

    if enable_foreign_keys:
        # NOTE: Raw SQL is necessary here because SQLAlchemy doesn't provide
        # a built-in abstraction for SQLite PRAGMA commands. These are SQLite-specific
        # configuration commands that must be executed as raw SQL.
        cursor.execute("PRAGMA foreign_keys = ON")

    if journal_mode:
        # NOTE: Raw SQL is necessary for PRAGMA commands (see comment above)
        cursor.execute(f"PRAGMA journal_mode = {journal_mode}")

    cursor.close()
