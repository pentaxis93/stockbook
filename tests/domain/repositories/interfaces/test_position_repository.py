"""Tests for Position repository interface.

This module tests the IPositionRepository interface contract to ensure it defines
proper abstractions for position data persistence operations in the domain layer.
"""

from abc import ABC
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from src.domain.entities.position import Position
from src.domain.repositories.interfaces.position_repository import IPositionRepository
from src.domain.value_objects.money import Money
from src.domain.value_objects.quantity import Quantity

UTC = ZoneInfo("UTC")


class MockPositionRepository(IPositionRepository):
    """Mock implementation of IPositionRepository for contract testing."""

    def __init__(self) -> None:
        self.positions: dict[str, Position] = {}
        self.next_id = 1

    def create(self, position: Position) -> str:
        """Create a new position and return its ID."""
        position_id = f"position-{self.next_id}"
        self.next_id += 1
        self.positions[position_id] = position
        return position_id

    def update(self, position_id: str, position: Position) -> bool:
        """Update existing position."""
        if position_id in self.positions:
            self.positions[position_id] = position
            return True
        return False

    def get_by_id(self, position_id: str) -> Position | None:
        """Retrieve position by ID."""
        return self.positions.get(position_id)

    def get_by_portfolio_and_stock(
        self,
        portfolio_id: str,
        stock_id: str,
    ) -> Position | None:
        """Retrieve position by portfolio and stock combination."""
        for position in self.positions.values():
            if position.portfolio_id == portfolio_id and position.stock_id == stock_id:
                return position
        return None

    def get_by_portfolio(self, portfolio_id: str) -> list[Position]:
        """Retrieve all positions for a specific portfolio."""
        return [
            position
            for position in self.positions.values()
            if position.portfolio_id == portfolio_id
        ]

    def delete(self, position_id: str) -> bool:
        """Delete position by ID."""
        if position_id in self.positions:
            del self.positions[position_id]
            return True
        return False

    def delete_by_portfolio_and_stock(
        self,
        portfolio_id: str,
        stock_id: str,
    ) -> bool:
        """Delete position by portfolio and stock combination."""
        for position_id, position in list(self.positions.items()):
            if position.portfolio_id == portfolio_id and position.stock_id == stock_id:
                del self.positions[position_id]
                return True
        return False


def create_test_position(
    portfolio_id: str = "portfolio-1",
    stock_id: str = "stock-1",
    quantity: int = 100,
    average_cost: str = "150.00",
    position_id: str | None = None,
) -> Position:
    """Helper to create test position entity."""
    builder = (
        Position.Builder()
        .with_portfolio_id(portfolio_id)
        .with_stock_id(stock_id)
        .with_quantity(Quantity(quantity))
        .with_average_cost(Money(Decimal(average_cost)))
        .with_last_transaction_date(datetime.now(UTC))
    )
    if position_id:
        builder = builder.with_id(position_id)
    return builder.build()


class TestPositionRepositoryContract:
    """Test that IPositionRepository interface is properly defined as abstract."""

    def test_position_repository_is_abstract(self) -> None:
        """Should not be able to instantiate IPositionRepository directly."""
        with pytest.raises(TypeError):
            _ = IPositionRepository()  # type: ignore[abstract]

    def test_position_repository_inherits_from_abc(self) -> None:
        """Should verify IPositionRepository inherits from ABC."""
        assert issubclass(IPositionRepository, ABC)

    def test_position_repository_has_abstract_methods(self) -> None:
        """Should verify IPositionRepository has abstract methods."""
        assert hasattr(IPositionRepository, "__abstractmethods__")
        assert len(IPositionRepository.__abstractmethods__) > 0

    def test_position_repository_method_signatures(self) -> None:
        """Should verify all required methods exist on interface."""
        required_methods = [
            "create",
            "update",
            "get_by_id",
            "get_by_portfolio_and_stock",
            "get_by_portfolio",
            "delete",
            "delete_by_portfolio_and_stock",
        ]

        for method_name in required_methods:
            assert hasattr(IPositionRepository, method_name)


class TestPositionRepositoryContractImplementation:
    """Test the IPositionRepository contract implementation."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repository = MockPositionRepository()
        self.test_position = create_test_position()

    def test_create_returns_position_id(self) -> None:
        """Should return position ID when creating a position."""
        position_id = self.repository.create(self.test_position)

        assert isinstance(position_id, str)
        assert len(position_id) > 0

    def test_get_by_id_returns_position_when_exists(self) -> None:
        """Should return position when querying by existing ID."""
        position_id = self.repository.create(self.test_position)
        retrieved_position = self.repository.get_by_id(position_id)

        assert retrieved_position is not None
        assert retrieved_position.portfolio_id == self.test_position.portfolio_id
        assert retrieved_position.stock_id == self.test_position.stock_id
        assert retrieved_position.quantity.value == self.test_position.quantity.value

    def test_get_by_id_returns_none_when_not_exists(self) -> None:
        """Should return None when querying by non-existent ID."""
        retrieved_position = self.repository.get_by_id("non-existent-id")

        assert retrieved_position is None

    def test_get_by_portfolio_and_stock_returns_position_when_exists(self) -> None:
        """Should return position when querying by portfolio and stock."""
        _ = self.repository.create(self.test_position)
        retrieved_position = self.repository.get_by_portfolio_and_stock(
            self.test_position.portfolio_id,
            self.test_position.stock_id,
        )

        assert retrieved_position is not None
        assert retrieved_position.portfolio_id == self.test_position.portfolio_id
        assert retrieved_position.stock_id == self.test_position.stock_id

    def test_get_by_portfolio_and_stock_returns_none_when_not_exists(self) -> None:
        """Should return None when querying by non-existent portfolio and stock."""
        retrieved_position = self.repository.get_by_portfolio_and_stock(
            "non-existent-portfolio",
            "non-existent-stock",
        )

        assert retrieved_position is None

    def test_get_by_portfolio_returns_positions_for_portfolio(self) -> None:
        """Should return all positions for a specific portfolio."""
        position1 = create_test_position("portfolio-1", "stock-1")
        position2 = create_test_position("portfolio-1", "stock-2")
        position3 = create_test_position("portfolio-2", "stock-1")

        _ = self.repository.create(position1)
        _ = self.repository.create(position2)
        _ = self.repository.create(position3)

        portfolio_positions = self.repository.get_by_portfolio("portfolio-1")

        assert len(portfolio_positions) == 2
        stock_ids = {pos.stock_id for pos in portfolio_positions}
        assert stock_ids == {"stock-1", "stock-2"}

    def test_get_by_portfolio_returns_empty_list_when_no_positions(self) -> None:
        """Should return empty list when portfolio has no positions."""
        positions = self.repository.get_by_portfolio("non-existent-portfolio")

        assert positions == []

    def test_update_returns_true_when_successful(self) -> None:
        """Should return True when update is successful."""
        position_id = self.repository.create(self.test_position)
        updated_position = create_test_position(
            "portfolio-1",
            "stock-1",
            200,
            "175.00",
        )

        result = self.repository.update(position_id, updated_position)

        assert result is True
        retrieved_position = self.repository.get_by_id(position_id)
        assert retrieved_position is not None
        assert retrieved_position.quantity.value == 200
        assert retrieved_position.average_cost.amount == Decimal("175.00")

    def test_update_returns_false_when_position_not_exists(self) -> None:
        """Should return False when updating non-existent position."""
        updated_position = create_test_position()

        result = self.repository.update("non-existent-id", updated_position)

        assert result is False

    def test_delete_returns_true_when_successful(self) -> None:
        """Should return True when deletion is successful."""
        position_id = self.repository.create(self.test_position)

        result = self.repository.delete(position_id)

        assert result is True
        assert self.repository.get_by_id(position_id) is None

    def test_delete_returns_false_when_position_not_exists(self) -> None:
        """Should return False when deleting non-existent position."""
        result = self.repository.delete("non-existent-id")

        assert result is False

    def test_delete_by_portfolio_and_stock_returns_true_when_successful(self) -> None:
        """Should return True when deletion by portfolio and stock is successful."""
        _ = self.repository.create(self.test_position)

        result = self.repository.delete_by_portfolio_and_stock(
            self.test_position.portfolio_id,
            self.test_position.stock_id,
        )

        assert result is True
        retrieved_position = self.repository.get_by_portfolio_and_stock(
            self.test_position.portfolio_id,
            self.test_position.stock_id,
        )
        assert retrieved_position is None

    def test_delete_by_portfolio_and_stock_returns_false_when_not_exists(self) -> None:
        """Should return False when deleting non-existent position."""
        result = self.repository.delete_by_portfolio_and_stock(
            "non-existent-portfolio",
            "non-existent-stock",
        )

        assert result is False


class TestPositionRepositoryContractEdgeCases:
    """Test edge cases and boundary conditions for position repository contract."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repository = MockPositionRepository()

    def test_repository_handles_empty_collections(self) -> None:
        """Should handle operations on empty repositories."""
        assert self.repository.get_by_portfolio("any-portfolio") == []
        assert self.repository.get_by_id("any-id") is None
        assert (
            self.repository.get_by_portfolio_and_stock("any-portfolio", "any-stock")
            is None
        )

    def test_repository_handles_invalid_parameters(self) -> None:
        """Should handle invalid parameter values gracefully."""
        # These should not raise exceptions but return appropriate values
        assert self.repository.get_by_id("") is None
        assert self.repository.get_by_portfolio("") == []
        assert self.repository.get_by_portfolio_and_stock("", "") is None

    def test_multiple_positions_same_portfolio_different_stocks(self) -> None:
        """Should handle multiple positions in same portfolio for different stocks."""
        position1 = create_test_position("portfolio-1", "stock-1", 100, "150.00")
        position2 = create_test_position("portfolio-1", "stock-2", 200, "175.00")
        position3 = create_test_position("portfolio-1", "stock-3", 50, "200.00")

        _ = self.repository.create(position1)
        _ = self.repository.create(position2)
        _ = self.repository.create(position3)

        portfolio_positions = self.repository.get_by_portfolio("portfolio-1")

        assert len(portfolio_positions) == 3
        stock_ids = {pos.stock_id for pos in portfolio_positions}
        assert stock_ids == {"stock-1", "stock-2", "stock-3"}

    def test_same_stock_different_portfolios(self) -> None:
        """Should handle same stock in different portfolios."""
        position1 = create_test_position("portfolio-1", "stock-1", 100, "150.00")
        position2 = create_test_position("portfolio-2", "stock-1", 200, "175.00")

        _ = self.repository.create(position1)
        _ = self.repository.create(position2)

        portfolio1_positions = self.repository.get_by_portfolio("portfolio-1")
        portfolio2_positions = self.repository.get_by_portfolio("portfolio-2")

        assert len(portfolio1_positions) == 1
        assert len(portfolio2_positions) == 1
        assert portfolio1_positions[0].portfolio_id == "portfolio-1"
        assert portfolio2_positions[0].portfolio_id == "portfolio-2"
        assert portfolio1_positions[0].stock_id == "stock-1"
        assert portfolio2_positions[0].stock_id == "stock-1"

    def test_delete_by_portfolio_and_stock_with_multiple_positions(self) -> None:
        """Should delete only the specific position when multiple exist."""
        position1 = create_test_position("portfolio-1", "stock-1", 100, "150.00")
        position2 = create_test_position("portfolio-1", "stock-2", 200, "175.00")
        position3 = create_test_position("portfolio-2", "stock-1", 50, "200.00")

        _ = self.repository.create(position1)
        _ = self.repository.create(position2)
        _ = self.repository.create(position3)

        # Delete position1
        result = self.repository.delete_by_portfolio_and_stock("portfolio-1", "stock-1")

        assert result is True
        remaining_positions = self.repository.get_by_portfolio("portfolio-1")
        assert len(remaining_positions) == 1
        assert remaining_positions[0].stock_id == "stock-2"

        # Other portfolios should be unaffected
        portfolio2_positions = self.repository.get_by_portfolio("portfolio-2")
        assert len(portfolio2_positions) == 1
        assert portfolio2_positions[0].stock_id == "stock-1"


class TestPositionRepositoryContractPerformance:
    """Test performance characteristics of position repository contract."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repository = MockPositionRepository()

    def test_bulk_operations_efficiency(self) -> None:
        """Should handle bulk operations efficiently."""
        # Create many positions
        positions: list[Position] = []
        for i in range(10):
            for j in range(10):
                position = create_test_position(
                    f"portfolio-{i}",
                    f"stock-{j}",
                    100 + i * 10 + j,
                    "150.00",
                )
                positions.append(position)
                _ = self.repository.create(position)

        # Test bulk retrieval by portfolio
        portfolio_positions = self.repository.get_by_portfolio("portfolio-0")
        assert len(portfolio_positions) == 10

        # Test individual lookups
        for j in range(10):
            position = self.repository.get_by_portfolio_and_stock(
                "portfolio-0",
                f"stock-{j}",
            )
            assert position is not None

    def test_search_operations_scalability(self) -> None:
        """Should maintain search performance with larger datasets."""
        # Create positions with different patterns
        for i in range(50):
            position = create_test_position(
                f"portfolio-{i % 5}",
                f"stock-{i % 10}",
                100 + i,
                "150.00",
            )
            _ = self.repository.create(position)

        # Test portfolio-based queries
        for portfolio_id in range(5):
            portfolio_positions = self.repository.get_by_portfolio(
                f"portfolio-{portfolio_id}",
            )
            # Each portfolio should have 10 positions (50 total / 5 portfolios)
            assert len(portfolio_positions) == 10

        # Test stock-based queries across portfolios
        for stock_id in range(10):
            found_positions = 0
            for portfolio_id in range(5):
                position = self.repository.get_by_portfolio_and_stock(
                    f"portfolio-{portfolio_id}",
                    f"stock-{stock_id}",
                )
                if position:
                    found_positions += 1
            # Each stock should be found in 1 or more portfolios
            assert found_positions >= 1
