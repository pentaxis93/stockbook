"""SQLite-specific database configuration.

This module contains SQLite-specific settings and configurations
that are separated from the main database factory to maintain
database independence.
"""

# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool


def configure_sqlite_engine(engine: Engine) -> None:
    """Configure SQLite-specific settings on an engine.

    Args:
        engine: SQLAlchemy engine to configure
    """

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn: Any, connection_record: Any) -> None:
        """Configure SQLite pragmas on each connection."""
        # connection_record is required by SQLAlchemy but not used
        _ = connection_record
        configure_sqlite_connection(dbapi_conn)

    # Mark function as used by SQLAlchemy event system
    _ = set_sqlite_pragma


def configure_sqlite_connection(
    connection: Any,
    *,
    enable_foreign_keys: bool = True,
    journal_mode: str | None = None,
) -> None:
    """Configure SQLite PRAGMA settings on a connection.

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


def get_sqlite_engine_kwargs(database_url: str) -> dict[str, Any]:
    """Get SQLite-specific engine configuration.

    Args:
        database_url: Database URL

    Returns:
        Dictionary of engine kwargs specific to SQLite
    """
    kwargs: dict[str, Any] = {
        "connect_args": {"check_same_thread": False},
    }

    # Special configuration for in-memory databases
    if database_url == "sqlite:///:memory:":
        # Use StaticPool for in-memory databases to share connection
        kwargs["poolclass"] = StaticPool

    return kwargs
