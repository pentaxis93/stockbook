"""Shared utilities for table definitions.

This module provides factory functions for common column patterns
to reduce duplication across table definitions while maintaining
clarity and type safety.
"""

from typing import Any

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, String, text


def id_column() -> Column[Any]:
    """Create a standard ID column."""
    return Column("id", String, primary_key=True, nullable=False)


def foreign_key_column(
    column_name: str,
    referenced_table: str,
    *,
    nullable: bool = False,
) -> Column[Any]:
    """Create a foreign key column.

    Args:
        column_name: Name of the column
        referenced_table: Name of the referenced table (without .id suffix)
        nullable: Whether the foreign key can be null

    Returns:
        Column with foreign key constraint
    """
    return Column(
        column_name,
        String,
        ForeignKey(f"{referenced_table}.id"),
        nullable=nullable,
    )


def timestamp_columns() -> list[Column[Any]]:
    """Create standard created_at and updated_at columns.

    Returns:
        List containing created_at and updated_at columns
    """
    return [
        Column(
            "created_at",
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
        Column(
            "updated_at",
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    ]


def enum_check_constraint(
    column_name: str,
    allowed_values: list[str],
    constraint_name: str,
) -> CheckConstraint:
    """Create a check constraint for enum-like columns.

    Args:
        column_name: Name of the column to constrain
        allowed_values: List of allowed values
        constraint_name: Name for the constraint

    Returns:
        CheckConstraint for the column
    """
    values_str = ", ".join(f"'{value}'" for value in allowed_values)
    return CheckConstraint(f"{column_name} IN ({values_str})", name=constraint_name)
