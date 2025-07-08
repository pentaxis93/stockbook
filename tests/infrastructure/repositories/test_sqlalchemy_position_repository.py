"""Tests for SqlAlchemyPositionRepository implementation."""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from src.domain.entities.position import Position
from src.domain.repositories.interfaces import IPositionRepository
from src.domain.value_objects.money import Money
from src.domain.value_objects.quantity import Quantity
from src.infrastructure.persistence.interfaces import IDatabaseConnection
from src.infrastructure.repositories.sqlalchemy_position_repository import (
    SqlAlchemyPositionRepository,
)


class TestSqlAlchemyPositionRepository:
    """Test suite for SqlAlchemyPositionRepository."""

    @pytest.fixture
    def mock_connection(self) -> Mock:
        """Create a mock database connection."""
        return Mock(spec=IDatabaseConnection)

    @pytest.fixture
    def position_repository(
        self,
        mock_connection: Mock,
    ) -> SqlAlchemyPositionRepository:
        """Create a position repository with mock connection."""
        return SqlAlchemyPositionRepository(mock_connection)

    @pytest.fixture
    def sample_position(self) -> Position:
        """Create a sample position for testing."""
        return (
            Position.Builder()
            .with_id("pos-123")
            .with_portfolio_id("portfolio-456")
            .with_stock_id("stock-789")
            .with_quantity(Quantity(Decimal("100.0000")))
            .with_average_cost(Money(Decimal("50.00")))
            .with_last_transaction_date(datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC))
            .build()
        )

    def test_repository_implements_interface(
        self,
        position_repository: SqlAlchemyPositionRepository,
    ) -> None:
        """Test that repository implements IPositionRepository interface."""
        assert isinstance(position_repository, IPositionRepository)

    def test_create_inserts_new_position(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
        sample_position: Position,
    ) -> None:
        """Test that create inserts a new position."""
        result = position_repository.create(sample_position)

        assert result == "pos-123"
        mock_connection.execute.assert_called_once()

        # Verify the SQL statement was an INSERT
        call_args = mock_connection.execute.call_args[0][0]
        assert hasattr(call_args, "table")
        assert call_args.table.name == "positions"

    def test_create_raises_value_error_on_unique_constraint_violation(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
        sample_position: Position,
    ) -> None:
        """Test that create raises ValueError when unique constraint is violated."""
        # Mock an integrity error with our unique constraint name
        mock_connection.execute.side_effect = IntegrityError(
            "statement",
            "params",
            Exception("uq_portfolio_stock_position violation"),
        )

        with pytest.raises(
            ValueError,
            match=(
                "Position for portfolio portfolio-456 and stock stock-789 "
                "already exists"
            ),
        ):
            _ = position_repository.create(sample_position)

    def test_create_re_raises_unexpected_integrity_error(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
        sample_position: Position,
    ) -> None:
        """Test that create re-raises unexpected IntegrityError."""
        # Mock an integrity error that's not our unique constraint
        mock_connection.execute.side_effect = IntegrityError(
            "statement",
            "params",
            Exception("some other constraint violation"),
        )

        with pytest.raises(IntegrityError):
            _ = position_repository.create(sample_position)

    def test_update_modifies_existing_position(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
        sample_position: Position,
    ) -> None:
        """Test that update modifies an existing position."""
        # Mock successful update (1 row affected)
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_connection.execute.return_value = mock_result

        result = position_repository.update("pos-123", sample_position)

        assert result is True
        mock_connection.execute.assert_called_once()

    def test_update_returns_false_when_position_not_found(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
        sample_position: Position,
    ) -> None:
        """Test that update returns False when position not found."""
        # Mock no rows affected
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_connection.execute.return_value = mock_result

        result = position_repository.update("non-existent", sample_position)

        assert result is False

    def test_update_raises_value_error_on_unique_constraint_violation(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
        sample_position: Position,
    ) -> None:
        """Test that update raises ValueError when unique constraint is violated."""
        # Mock an integrity error with our unique constraint name
        mock_connection.execute.side_effect = IntegrityError(
            "statement",
            "params",
            Exception("uq_portfolio_stock_position violation"),
        )

        with pytest.raises(
            ValueError,
            match=(
                "Position for portfolio portfolio-456 and stock stock-789 "
                "already exists"
            ),
        ):
            _ = position_repository.update("pos-123", sample_position)

    def test_update_re_raises_unexpected_integrity_error(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
        sample_position: Position,
    ) -> None:
        """Test that update re-raises unexpected IntegrityError."""
        # Mock an integrity error that's not our unique constraint
        mock_connection.execute.side_effect = IntegrityError(
            "statement",
            "params",
            Exception("some other constraint violation"),
        )

        with pytest.raises(IntegrityError):
            _ = position_repository.update("pos-123", sample_position)

    def test_get_by_id_returns_position_when_found(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
    ) -> None:
        """Test that get_by_id returns position when found."""
        # Mock database row
        mock_row = Mock()
        mock_row._asdict.return_value = {
            "id": "pos-123",
            "portfolio_id": "portfolio-456",
            "stock_id": "stock-789",
            "quantity": Decimal("100.0000"),
            "average_cost": Decimal("50.00"),
            "last_transaction_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
        }

        mock_result = Mock()
        mock_result.fetchone.return_value = mock_row
        mock_connection.execute.return_value = mock_result

        position = position_repository.get_by_id("pos-123")

        assert position is not None
        assert position.id == "pos-123"
        assert position.portfolio_id == "portfolio-456"
        assert position.stock_id == "stock-789"
        assert position.quantity == Quantity(Decimal("100.0000"))
        assert position.average_cost == Money(Decimal("50.00"))

    def test_get_by_id_returns_none_when_not_found(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
    ) -> None:
        """Test that get_by_id returns None when position not found."""
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_connection.execute.return_value = mock_result

        position = position_repository.get_by_id("non-existent")

        assert position is None

    def test_get_by_portfolio_returns_positions_for_portfolio(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
    ) -> None:
        """Test that get_by_portfolio returns all positions for a portfolio."""
        # Mock multiple database rows
        mock_row1 = Mock()
        mock_row1._asdict.return_value = {
            "id": "pos-1",
            "portfolio_id": "portfolio-456",
            "stock_id": "stock-789",
            "quantity": Decimal("100.0000"),
            "average_cost": Decimal("50.00"),
            "last_transaction_date": None,
        }

        mock_row2 = Mock()
        mock_row2._asdict.return_value = {
            "id": "pos-2",
            "portfolio_id": "portfolio-456",
            "stock_id": "stock-abc",
            "quantity": Decimal("200.0000"),
            "average_cost": Decimal("25.00"),
            "last_transaction_date": None,
        }

        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row1, mock_row2]
        mock_connection.execute.return_value = mock_result

        positions = position_repository.get_by_portfolio("portfolio-456")

        assert len(positions) == 2
        position_ids = {p.id for p in positions}
        assert position_ids == {"pos-1", "pos-2"}

    def test_get_by_portfolio_returns_empty_list_when_no_positions(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
    ) -> None:
        """Test that get_by_portfolio returns empty list when no positions found."""
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_connection.execute.return_value = mock_result

        positions = position_repository.get_by_portfolio("non-existent-portfolio")

        assert positions == []

    def test_get_by_portfolio_and_stock_returns_position_when_found(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
    ) -> None:
        """Test that get_by_portfolio_and_stock returns position when found."""
        # Mock database row
        mock_row = Mock()
        mock_row._asdict.return_value = {
            "id": "pos-123",
            "portfolio_id": "portfolio-456",
            "stock_id": "stock-789",
            "quantity": Decimal("100.0000"),
            "average_cost": Decimal("50.00"),
            "last_transaction_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
        }

        mock_result = Mock()
        mock_result.fetchone.return_value = mock_row
        mock_connection.execute.return_value = mock_result

        position = position_repository.get_by_portfolio_and_stock(
            "portfolio-456",
            "stock-789",
        )

        assert position is not None
        assert position.id == "pos-123"
        assert position.portfolio_id == "portfolio-456"
        assert position.stock_id == "stock-789"

    def test_get_by_portfolio_and_stock_returns_none_when_not_found(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
    ) -> None:
        """Test that get_by_portfolio_and_stock returns None when not found."""
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_connection.execute.return_value = mock_result

        position = position_repository.get_by_portfolio_and_stock(
            "non-existent-portfolio",
            "non-existent-stock",
        )

        assert position is None

    def test_delete_removes_position_and_returns_true(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
    ) -> None:
        """Test that delete removes position and returns True when successful."""
        # Mock successful deletion (1 row affected)
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_connection.execute.return_value = mock_result

        result = position_repository.delete("pos-123")

        assert result is True
        mock_connection.execute.assert_called_once()

    def test_delete_returns_false_when_position_not_found(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
    ) -> None:
        """Test that delete returns False when position not found."""
        # Mock no rows affected
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_connection.execute.return_value = mock_result

        result = position_repository.delete("non-existent")

        assert result is False

    def test_delete_by_portfolio_and_stock_removes_position(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
    ) -> None:
        """Test that delete_by_portfolio_and_stock removes position."""
        # Mock successful deletion (1 row affected)
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_connection.execute.return_value = mock_result

        result = position_repository.delete_by_portfolio_and_stock(
            "portfolio-456",
            "stock-789",
        )

        assert result is True
        mock_connection.execute.assert_called_once()

    def test_delete_by_portfolio_and_stock_returns_false_when_not_found(
        self,
        position_repository: SqlAlchemyPositionRepository,
        mock_connection: Mock,
    ) -> None:
        """Test that delete_by_portfolio_and_stock returns False when not found."""
        # Mock no rows affected
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_connection.execute.return_value = mock_result

        result = position_repository.delete_by_portfolio_and_stock(
            "non-existent-portfolio",
            "non-existent-stock",
        )

        assert result is False

    def test_entity_to_row_converts_position_to_dict(
        self,
        position_repository: SqlAlchemyPositionRepository,
        sample_position: Position,
    ) -> None:
        """Test that entity_to_row converts Position entity to database row."""
        row = position_repository.entity_to_row(sample_position)

        assert row["id"] == "pos-123"
        assert row["portfolio_id"] == "portfolio-456"
        assert row["stock_id"] == "stock-789"
        assert row["quantity"] == Decimal("100.0000")
        assert row["average_cost"] == Decimal("50.00")
        assert row["last_transaction_date"] == datetime(
            2024,
            1,
            15,
            10,
            30,
            0,
            tzinfo=UTC,
        )
        assert "created_at" in row
        assert "updated_at" in row

    def test_entity_to_row_handles_none_last_transaction_date(
        self,
        position_repository: SqlAlchemyPositionRepository,
    ) -> None:
        """Test that entity_to_row handles None last_transaction_date."""
        position = (
            Position.Builder()
            .with_id("pos-123")
            .with_portfolio_id("portfolio-456")
            .with_stock_id("stock-789")
            .with_quantity(Quantity(Decimal("100.0000")))
            .with_average_cost(Money(Decimal("50.00")))
            .build()
        )

        row = position_repository.entity_to_row(position)

        assert row["last_transaction_date"] is None

    def test_row_to_entity_converts_database_row_to_position(
        self,
        position_repository: SqlAlchemyPositionRepository,
    ) -> None:
        """Test that row_to_entity converts database row to Position entity."""
        row = {
            "id": "pos-123",
            "portfolio_id": "portfolio-456",
            "stock_id": "stock-789",
            "quantity": Decimal("100.5000"),
            "average_cost": Decimal("45.75"),
            "last_transaction_date": datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
        }

        position = position_repository.row_to_entity(row)

        assert position.id == "pos-123"
        assert position.portfolio_id == "portfolio-456"
        assert position.stock_id == "stock-789"
        assert position.quantity == Quantity(Decimal("100.5000"))
        assert position.average_cost == Money(Decimal("45.75"))
        assert position.last_transaction_date == datetime(
            2024,
            1,
            15,
            10,
            30,
            0,
            tzinfo=UTC,
        )

    def test_row_to_entity_handles_none_last_transaction_date(
        self,
        position_repository: SqlAlchemyPositionRepository,
    ) -> None:
        """Test that row_to_entity handles None last_transaction_date."""
        row = {
            "id": "pos-123",
            "portfolio_id": "portfolio-456",
            "stock_id": "stock-789",
            "quantity": Decimal("100.0000"),
            "average_cost": Decimal("50.00"),
            "last_transaction_date": None,
        }

        position = position_repository.row_to_entity(row)

        assert position.last_transaction_date is None


class TestSqlAlchemyPositionRepositoryIntegration:
    """Integration tests for SqlAlchemyPositionRepository with real database."""

    @pytest.fixture
    def position_repository(
        self,
        test_db: Path,
    ) -> SqlAlchemyPositionRepository:
        """Create a position repository with test database."""
        import sqlalchemy as sa

        from src.infrastructure.persistence.tables import metadata

        # Create engine and all tables
        engine = sa.create_engine(f"sqlite:///{test_db}")
        metadata.create_all(engine)

        # Create a connection wrapper that implements IDatabaseConnection
        class DatabaseConnectionWrapper(IDatabaseConnection):
            def __init__(self, engine: Engine) -> None:
                self._engine = engine
                self._connection = engine.connect()

            def execute(
                self,
                statement: Any,
                parameters: dict[str, Any] | list[dict[str, Any]] | None = None,
                execution_options: dict[str, Any] | None = None,  # noqa: ARG002
            ) -> Any:
                # SQLAlchemy connection execute method has different signature
                if parameters is not None:
                    return self._connection.execute(statement, parameters)
                return self._connection.execute(statement)

            def commit(self) -> None:
                pass

            def rollback(self) -> None:
                pass

            def __del__(self) -> None:
                if hasattr(self, "_connection"):
                    self._connection.close()

        connection = DatabaseConnectionWrapper(engine)
        return SqlAlchemyPositionRepository(connection)

    @pytest.fixture
    def sample_position(self) -> Position:
        """Create a sample position for testing."""
        return (
            Position.Builder()
            .with_id("pos-123")
            .with_portfolio_id("portfolio-456")
            .with_stock_id("stock-789")
            .with_quantity(Quantity(Decimal("100.0000")))
            .with_average_cost(Money(Decimal("50.00")))
            .with_last_transaction_date(datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC))
            .build()
        )

    def test_create_and_retrieve_position(
        self,
        position_repository: SqlAlchemyPositionRepository,
        sample_position: Position,
        test_db: Path,
    ) -> None:
        """Test creating and retrieving a position with real database."""
        # Setup required data
        import sqlalchemy as sa

        engine = sa.create_engine(f"sqlite:///{test_db}")
        self._setup_test_data(engine)

        # Create position
        position_id = position_repository.create(sample_position)
        assert position_id == "pos-123"

        # Retrieve position
        retrieved_position = position_repository.get_by_id("pos-123")
        assert retrieved_position is not None
        assert retrieved_position.id == "pos-123"
        assert retrieved_position.portfolio_id == "portfolio-456"
        assert retrieved_position.stock_id == "stock-789"
        assert retrieved_position.quantity == Quantity(Decimal("100.0000"))

    def test_unique_constraint_enforcement(
        self,
        position_repository: SqlAlchemyPositionRepository,
        test_db: Path,
    ) -> None:
        """Test that unique constraint on portfolio_id + stock_id is enforced."""
        # Setup required data
        import sqlalchemy as sa

        engine = sa.create_engine(f"sqlite:///{test_db}")
        self._setup_test_data(engine)

        # Create first position
        position1 = (
            Position.Builder()
            .with_id("pos-1")
            .with_portfolio_id("portfolio-456")
            .with_stock_id("stock-789")
            .with_quantity(Quantity(Decimal("100.0000")))
            .with_average_cost(Money(Decimal("50.00")))
            .build()
        )
        _ = position_repository.create(position1)

        # Try to create second position with same portfolio_id + stock_id
        position2 = (
            Position.Builder()
            .with_id("pos-2")  # Different ID
            .with_portfolio_id("portfolio-456")  # Same portfolio
            .with_stock_id("stock-789")  # Same stock
            .with_quantity(Quantity(Decimal("200.0000")))
            .with_average_cost(Money(Decimal("25.00")))
            .build()
        )

        # Should raise ValueError due to unique constraint
        with pytest.raises(
            ValueError,
            match=(
                "Position for portfolio portfolio-456 and stock stock-789 "
                "already exists"
            ),
        ):
            _ = position_repository.create(position2)

    def _setup_test_data(self, engine: Engine) -> None:
        """Setup required test data (portfolios and stocks)."""
        from src.infrastructure.persistence.tables.portfolio_table import (
            portfolio_table,
        )
        from src.infrastructure.persistence.tables.stock_table import stock_table

        with engine.connect() as conn:
            with conn.begin():
                # Insert required portfolio
                _ = conn.execute(
                    portfolio_table.insert().values(
                        id="portfolio-456",
                        name="Test Portfolio",
                        description="Test portfolio for position tests",
                    ),
                )

                # Insert another portfolio for multi-portfolio tests
                _ = conn.execute(
                    portfolio_table.insert().values(
                        id="portfolio-789",
                        name="Another Portfolio",
                        description="Another test portfolio",
                    ),
                )

                # Insert required stocks
                _ = conn.execute(
                    stock_table.insert().values(
                        id="stock-789",
                        symbol="AAPL",
                        company_name="Apple Inc.",
                    ),
                )

                _ = conn.execute(
                    stock_table.insert().values(
                        id="stock-abc",
                        symbol="GOOGL",
                        company_name="Alphabet Inc.",
                    ),
                )
