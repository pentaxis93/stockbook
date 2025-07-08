"""SQLAlchemy implementation of the Position repository."""

# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportArgumentType=false

from typing import Any

from sqlalchemy import delete as sql_delete
from sqlalchemy import exc, insert, select
from sqlalchemy import update as sql_update

from src.domain.entities.position import Position
from src.domain.repositories.interfaces import IPositionRepository
from src.domain.value_objects.money import Money
from src.domain.value_objects.quantity import Quantity
from src.infrastructure.persistence.interfaces import IDatabaseConnection
from src.infrastructure.persistence.tables.position_table import position_table


class SqlAlchemyPositionRepository(IPositionRepository):
    """SQLAlchemy implementation of position repository."""

    def __init__(self, connection: IDatabaseConnection) -> None:
        """Initialize the repository.

        Args:
            connection: Database connection supporting SQLAlchemy Core operations
        """
        self._connection = connection

    def create(self, position: Position) -> str:
        """Create a new position in the database.

        Args:
            position: Position entity to create

        Returns:
            ID of the created position

        Raises:
            ValueError: If a position with the same portfolio+stock already exists
            exc.DatabaseError: For other database errors
        """
        row_data = self.entity_to_row(position)

        stmt = insert(position_table).values(**row_data)

        try:
            self._connection.execute(stmt)
        except exc.IntegrityError as e:
            # Check if it's a unique constraint violation on portfolio_id + stock_id
            if (
                "UNIQUE constraint failed: positions.portfolio_id, positions.stock_id"
                in str(e)
                or "uq_portfolio_stock_position" in str(e)
            ):
                msg = (
                    f"Position for portfolio {position.portfolio_id} "
                    f"and stock {position.stock_id} already exists"
                )
                raise ValueError(msg) from e
            raise
        else:
            return position.id

    def update(self, position_id: str, position: Position) -> bool:
        """Update an existing position.

        Args:
            position_id: ID of the position to update
            position: Position entity with updated values

        Returns:
            True if position was updated, False if not found

        Raises:
            ValueError: If updating would violate unique constraints
            exc.DatabaseError: For other database errors
        """
        row_data = self.entity_to_row(position)
        # Remove fields that shouldn't be updated
        row_data.pop("id", None)
        row_data.pop("created_at", None)

        stmt = (
            sql_update(position_table)
            .where(position_table.c.id == position_id)
            .values(**row_data)
        )

        try:
            result = self._connection.execute(stmt)
            return bool(result.rowcount > 0)
        except exc.IntegrityError as e:
            if (
                "UNIQUE constraint failed: positions.portfolio_id, positions.stock_id"
                in str(e)
                or "uq_portfolio_stock_position" in str(e)
            ):
                msg = (
                    f"Position for portfolio {position.portfolio_id} "
                    f"and stock {position.stock_id} already exists"
                )
                raise ValueError(msg) from e
            raise

    def get_by_id(self, position_id: str) -> Position | None:
        """Retrieve position by ID.

        Args:
            position_id: Unique identifier of the position

        Returns:
            Position entity if found, None otherwise
        """
        stmt = select(*position_table.c).where(position_table.c.id == position_id)
        result = self._connection.execute(stmt)
        row = result.fetchone()

        if row is None:
            return None

        # Handle both dict (from mocks) and Row objects (from SQLAlchemy)
        row_dict = row._asdict() if hasattr(row, "_asdict") else row
        return self.row_to_entity(row_dict)

    def get_by_portfolio(self, portfolio_id: str) -> list[Position]:
        """Retrieve all positions for a specific portfolio.

        Args:
            portfolio_id: Portfolio identifier

        Returns:
            List of Position entities for the portfolio
        """
        stmt = select(*position_table.c).where(
            position_table.c.portfolio_id == portfolio_id,
        )
        result = self._connection.execute(stmt)
        rows = result.fetchall()

        return [
            self.row_to_entity(row._asdict() if hasattr(row, "_asdict") else row)
            for row in rows
        ]

    def get_by_portfolio_and_stock(
        self,
        portfolio_id: str,
        stock_id: str,
    ) -> Position | None:
        """Retrieve position by portfolio and stock combination.

        Args:
            portfolio_id: Portfolio identifier
            stock_id: Stock identifier

        Returns:
            Position entity if found, None otherwise
        """
        stmt = select(*position_table.c).where(
            (position_table.c.portfolio_id == portfolio_id)
            & (position_table.c.stock_id == stock_id),
        )
        result = self._connection.execute(stmt)
        row = result.fetchone()

        if row is None:
            return None

        # Handle both dict (from mocks) and Row objects (from SQLAlchemy)
        row_dict = row._asdict() if hasattr(row, "_asdict") else row
        return self.row_to_entity(row_dict)

    def delete(self, position_id: str) -> bool:
        """Delete a position by its ID.

        Args:
            position_id: Unique identifier of the position to delete

        Returns:
            True if deletion successful, False if position not found
        """
        stmt = sql_delete(position_table).where(position_table.c.id == position_id)
        result = self._connection.execute(stmt)
        return bool(result.rowcount > 0)

    def delete_by_portfolio_and_stock(
        self,
        portfolio_id: str,
        stock_id: str,
    ) -> bool:
        """Delete position by portfolio and stock combination.

        Args:
            portfolio_id: Portfolio identifier
            stock_id: Stock identifier

        Returns:
            True if deletion successful, False if position not found
        """
        stmt = sql_delete(position_table).where(
            (position_table.c.portfolio_id == portfolio_id)
            & (position_table.c.stock_id == stock_id),
        )
        result = self._connection.execute(stmt)
        return bool(result.rowcount > 0)

    def entity_to_row(self, position: Position) -> dict[str, Any]:
        """Convert Position entity to database row dictionary.

        Args:
            position: Position entity to convert

        Returns:
            Dictionary representing database row
        """
        from datetime import UTC, datetime

        now = datetime.now(UTC)

        return {
            "id": position.id,
            "portfolio_id": position.portfolio_id,
            "stock_id": position.stock_id,
            "quantity": position.quantity.value,
            "average_cost": position.average_cost.amount,
            "last_transaction_date": position.last_transaction_date,
            "created_at": now,
            "updated_at": now,
        }

    def row_to_entity(self, row: dict[str, Any]) -> Position:
        """Convert database row to Position entity.

        Args:
            row: Database row as dictionary

        Returns:
            Position entity
        """
        builder = (
            Position.Builder()
            .with_id(row["id"])
            .with_portfolio_id(row["portfolio_id"])
            .with_stock_id(row["stock_id"])
            .with_quantity(Quantity(row["quantity"]))
            .with_average_cost(Money(row["average_cost"]))
        )

        if row["last_transaction_date"] is not None:
            builder = builder.with_last_transaction_date(row["last_transaction_date"])

        return builder.build()
