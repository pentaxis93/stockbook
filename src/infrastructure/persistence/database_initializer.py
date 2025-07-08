"""Database initialization module.

This module provides functions to initialize the database schema,
creating all necessary tables if they don't already exist.
"""

import logging
from pathlib import Path

from sqlalchemy import MetaData
from sqlalchemy.engine import Engine

from src.infrastructure.persistence.database_factory import create_engine

# Import all tables to ensure they're registered with metadata
from src.infrastructure.persistence.tables import (
    journal_entry_table,
    metadata,
    portfolio_balance_table,
    portfolio_table,
    position_table,
    stock_table,
    target_table,
    transaction_table,
)

# These imports are needed to register tables with metadata
_ = journal_entry_table
_ = portfolio_balance_table
_ = portfolio_table
_ = position_table
_ = stock_table
_ = target_table
_ = transaction_table

logger = logging.getLogger(__name__)


def _collect_all_metadata() -> MetaData:
    """Collect all table metadata.

    Returns:
        MetaData: Combined metadata from all table definitions
    """
    # All tables share the same metadata instance
    return metadata


def _create_tables_if_not_exist(engine: Engine, table_metadata: MetaData) -> None:
    """Create all tables defined in the metadata if they don't exist.

    Args:
        engine: SQLAlchemy engine
        table_metadata: MetaData containing table definitions
    """
    # Create all tables - this is idempotent (won't recreate existing tables)
    table_metadata.create_all(engine)
    logger.info("Created/verified %d tables", len(table_metadata.tables))


def _extract_db_path(database_url: str) -> str:
    """Extract database path from URL or return path as-is."""
    if "://" in database_url:
        # It's a URL
        if database_url.startswith("sqlite:///"):
            return database_url.replace("sqlite:///", "")
        # For non-SQLite databases or invalid URLs
        msg = f"Unsupported database URL: {database_url}"
        raise ValueError(msg)
    # It's a file path
    return database_url


def _ensure_db_directory_exists(db_path: str) -> None:
    """Create database directory if it doesn't exist."""
    path = Path(db_path)
    parent_dir = path.parent
    if parent_dir != Path():
        parent_dir.mkdir(parents=True, exist_ok=True)


def initialize_database(
    database_url: str,
) -> None:
    """Initialize the database with all required tables.

    This function is idempotent - it can be called multiple times safely
    and will only create tables that don't already exist.

    Args:
        database_url: Database connection URL or file path

    Raises:
        Exception: If database initialization fails
    """
    try:
        logger.info("Initializing database: %s", database_url)

        # Extract database path from URL
        db_path = _extract_db_path(database_url)

        # Ensure directory exists
        _ensure_db_directory_exists(db_path)

        # Create engine using the factory which expects a path
        engine = create_engine(db_path)

        # Collect all metadata
        all_metadata = _collect_all_metadata()

        # Create tables if they don't exist
        _create_tables_if_not_exist(engine, all_metadata)

        # Dispose of the engine to close connections
        engine.dispose()

        logger.info("Database initialized successfully")

    except Exception:
        logger.exception("Failed to initialize database")
        raise
