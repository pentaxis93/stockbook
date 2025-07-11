"""Test suite for table utilities.

Tests the factory functions that provide common column patterns
for SQLAlchemy Core table definitions.
"""

import pytest
from sqlalchemy import (
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    create_engine,
    insert,
)

from src.infrastructure.persistence.tables.table_utils import (
    base_columns,
    enum_check_constraint,
    foreign_key_column,
    id_column,
    timestamp_columns,
)


class TestIdColumn:
    """Test id column factory function."""

    def test_creates_id_column_with_correct_properties(self) -> None:
        """Should create id column with correct type and constraints."""
        # Act
        column = id_column()

        # Assert
        assert column.name == "id"
        assert isinstance(column.type, String)
        assert column.primary_key is True
        assert column.nullable is False

    def test_id_column_in_table_definition(self) -> None:
        """Should work correctly in a table definition."""
        # Arrange
        metadata = MetaData()

        # Act
        test_table = Table(
            "test_table",
            metadata,
            id_column(),
            Column("name", String),
        )

        # Assert
        assert "id" in test_table.columns
        assert test_table.columns["id"].primary_key is True


class TestTimestampColumns:
    """Test timestamp columns factory function."""

    def test_creates_timestamp_columns_list(self) -> None:
        """Should create list with created_at and updated_at columns."""
        # Act
        columns = timestamp_columns()

        # Assert
        assert len(columns) == 2
        assert all(isinstance(col, Column) for col in columns)

    def test_created_at_column_properties(self) -> None:
        """Should create created_at column with correct properties."""
        # Act
        columns = timestamp_columns()
        created_at = columns[0]

        # Assert
        assert created_at.name == "created_at"
        assert isinstance(created_at.type, DateTime)
        assert created_at.nullable is False
        assert created_at.server_default is not None

    def test_updated_at_column_properties(self) -> None:
        """Should create updated_at column with correct properties."""
        # Act
        columns = timestamp_columns()
        updated_at = columns[1]

        # Assert
        assert updated_at.name == "updated_at"
        assert isinstance(updated_at.type, DateTime)
        assert updated_at.nullable is False
        assert updated_at.server_default is not None

    def test_timestamp_columns_in_table_definition(self) -> None:
        """Should work correctly when unpacked in table definition."""
        # Arrange
        metadata = MetaData()

        # Act
        test_table = Table(
            "test_table",
            metadata,
            Column("id", String, primary_key=True),
            *timestamp_columns(),
        )

        # Assert
        assert "created_at" in test_table.columns
        assert "updated_at" in test_table.columns


class TestBaseColumns:
    """Test base columns factory function."""

    def test_creates_all_base_columns(self) -> None:
        """Should create id, created_at, and updated_at columns."""
        # Act
        columns = base_columns()

        # Assert
        assert len(columns) == 3
        column_names = [col.name for col in columns]
        assert "id" in column_names
        assert "created_at" in column_names
        assert "updated_at" in column_names

    def test_base_columns_in_table_definition(self) -> None:
        """Should provide all common columns when used in table."""
        # Arrange
        metadata = MetaData()

        # Act
        test_table = Table(
            "test_table",
            metadata,
            *base_columns(),
            Column("name", String),
        )

        # Assert
        assert "id" in test_table.columns
        assert "created_at" in test_table.columns
        assert "updated_at" in test_table.columns
        assert test_table.columns["id"].primary_key is True

    def test_base_columns_order(self) -> None:
        """Should return columns in correct order: id, created_at, updated_at."""
        # Act
        columns = base_columns()

        # Assert
        assert columns[0].name == "id"
        assert columns[1].name == "created_at"
        assert columns[2].name == "updated_at"


class TestForeignKeyColumn:
    """Test foreign key column factory function."""

    def test_creates_non_nullable_foreign_key(self) -> None:
        """Should create non-nullable foreign key column by default."""
        # Act
        column = foreign_key_column("portfolio_id", "portfolios")

        # Assert
        assert column.name == "portfolio_id"
        assert isinstance(column.type, String)
        assert column.nullable is False
        assert len(column.foreign_keys) == 1

    def test_creates_nullable_foreign_key(self) -> None:
        """Should create nullable foreign key when specified."""
        # Act
        column = foreign_key_column("portfolio_id", "portfolios", nullable=True)

        # Assert
        assert column.nullable is True

    def test_foreign_key_references_correct_table(self) -> None:
        """Should reference the correct table's id column."""
        # Arrange
        metadata = MetaData()

        # Create referenced table first
        _ = Table(
            "stocks",
            metadata,
            Column("id", String, primary_key=True),
        )

        # Create table with foreign key
        test_table = Table(
            "test_table",
            metadata,
            Column("id", String, primary_key=True),
            foreign_key_column("stock_id", "stocks"),
        )

        # Assert
        fk_column = test_table.columns["stock_id"]
        fk = next(iter(fk_column.foreign_keys))
        assert fk.target_fullname == "stocks.id"

    def test_foreign_key_in_table_definition(self) -> None:
        """Should work correctly in table definition."""
        # Arrange
        metadata = MetaData()

        # Act
        test_table = Table(
            "test_table",
            metadata,
            Column("id", String, primary_key=True),
            foreign_key_column("portfolio_id", "portfolios"),
        )

        # Assert
        assert "portfolio_id" in test_table.columns
        assert len(test_table.columns["portfolio_id"].foreign_keys) == 1


class TestEnumCheckConstraint:
    """Test enum check constraint factory function."""

    def test_creates_check_constraint_with_values(self) -> None:
        """Should create check constraint with allowed values."""
        # Act
        constraint = enum_check_constraint(
            "status",
            ["active", "inactive", "pending"],
            "status_check",
        )

        # Assert
        assert constraint.name == "status_check"
        assert "status IN ('active', 'inactive', 'pending')" in str(constraint.sqltext)

    def test_constraint_in_table_definition(self) -> None:
        """Should work correctly in table definition."""
        # Arrange
        metadata = MetaData()

        # Act
        test_table = Table(
            "test_table",
            metadata,
            Column("id", String, primary_key=True),
            Column("status", String),
            enum_check_constraint("status", ["open", "closed"], "status_check"),
        )

        # Assert
        assert len(test_table.constraints) > 0
        check_constraints = [
            c for c in test_table.constraints if c.name == "status_check"
        ]
        assert len(check_constraints) == 1


class TestTableUtilsIntegration:
    """Integration tests for table utilities."""

    def test_complete_table_with_all_utilities(self) -> None:
        """Should create functional table using all utility functions."""
        # Arrange
        metadata = MetaData()

        # Act
        test_table = Table(
            "orders",
            metadata,
            *base_columns(),
            foreign_key_column("customer_id", "customers"),
            Column("status", String, nullable=False),
            Column("total_amount", String),
            enum_check_constraint("status", ["pending", "completed"], "status_check"),
        )

        # Assert
        assert (
            len(test_table.columns) == 6
        )  # id, created_at, updated_at, customer_id, status, total_amount
        assert test_table.columns["id"].primary_key is True
        assert "customer_id" in test_table.columns
        assert "status" in test_table.columns

    @pytest.mark.integration
    def test_table_creation_with_utilities(self) -> None:
        """Should successfully create table in database using utilities."""
        # Arrange
        metadata = MetaData()
        engine = create_engine("sqlite:///:memory:")

        test_table = Table(
            "test_entities",
            metadata,
            *base_columns(),
            Column("name", String, nullable=False),
        )

        # Act
        metadata.create_all(engine)

        # Assert - table created successfully
        from sqlalchemy import inspect

        inspector = inspect(engine)
        assert "test_entities" in inspector.get_table_names()

        # Test insert with auto-generated timestamps
        with engine.connect() as conn:  # type: ignore[var-annotated]
            conn.execute(  # type: ignore[no-untyped-call]
                insert(test_table).values(
                    id="test-id-1",
                    name="Test Entity",
                ),
            )
            conn.commit()  # type: ignore[no-untyped-call]
