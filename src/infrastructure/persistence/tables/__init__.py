"""SQLAlchemy table definitions using Core (not ORM)."""

from .stock_table import metadata, stock_table

__all__ = ["metadata", "stock_table"]
