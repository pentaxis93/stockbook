"""
Tests for StockApplicationService.

Following TDD approach - these tests define the expected behavior
of the application service that orchestrates stock operations.
"""

from unittest.mock import MagicMock, Mock

import pytest

from application.commands.stock_commands import CreateStockCommand
from application.dto.stock_dto import StockDto
from application.services.stock_application_service import \
    StockApplicationService
from domain.entities.stock_entity import StockEntity
from domain.events.stock_events import StockAddedEvent
from domain.repositories.interfaces import IStockRepository, IUnitOfWork
from domain.value_objects.stock_symbol import StockSymbol


class TestStockApplicationService:
    """Test suite for StockApplicationService."""

    def setup_method(self):
        """Set up test dependencies."""
        self.mock_stock_repository = Mock(spec=IStockRepository)
        self.mock_unit_of_work = Mock(spec=IUnitOfWork)
        self.mock_unit_of_work.stocks = self.mock_stock_repository

        # Make unit of work support context manager protocol
        self.mock_unit_of_work.__enter__ = Mock(return_value=self.mock_unit_of_work)
        self.mock_unit_of_work.__exit__ = Mock(return_value=None)

        self.service = StockApplicationService(self.mock_unit_of_work)

    def test_create_stock_with_valid_command(self):
        """Should create stock successfully with valid command."""
        # Arrange
        command = CreateStockCommand(
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes="Great company",
        )

        # Mock repository to return None (stock doesn't exist)
        self.mock_stock_repository.get_by_symbol.return_value = None
        self.mock_stock_repository.create.return_value = 123

        # Act
        result = self.service.create_stock(command)

        # Assert
        assert isinstance(result, StockDto)
        assert result.id == 123
        assert result.symbol == "AAPL"
        assert result.name == "Apple Inc."
        assert result.industry_group == "Technology"
        assert result.grade == "A"
        assert result.notes == "Great company"

        # Verify repository interactions
        self.mock_stock_repository.get_by_symbol.assert_called_once()
        self.mock_stock_repository.create.assert_called_once()
        self.mock_unit_of_work.commit.assert_called_once()

        # Verify the entity passed to repository
        create_call = self.mock_stock_repository.create.call_args[0][0]
        assert isinstance(create_call, StockEntity)
        assert str(create_call.symbol) == "AAPL"
        assert create_call.name == "Apple Inc."

    def test_create_stock_with_duplicate_symbol_raises_error(self):
        """Should raise error when trying to create stock with existing symbol."""
        # Arrange
        command = CreateStockCommand(symbol="AAPL", name="Apple Inc.")

        # Mock repository to return existing stock
        existing_stock = StockEntity(
            symbol=StockSymbol("AAPL"), name="Existing Apple Inc.", stock_id=456
        )
        self.mock_stock_repository.get_by_symbol.return_value = existing_stock

        # Act & Assert
        with pytest.raises(ValueError, match="Stock with symbol AAPL already exists"):
            self.service.create_stock(command)

        # Verify no creation was attempted
        self.mock_stock_repository.create.assert_not_called()
        self.mock_unit_of_work.commit.assert_not_called()

    def test_create_stock_handles_repository_error(self):
        """Should handle repository errors gracefully."""
        # Arrange
        command = CreateStockCommand(symbol="AAPL", name="Apple Inc.")

        self.mock_stock_repository.get_by_symbol.return_value = None
        self.mock_stock_repository.create.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            self.service.create_stock(command)

        # Verify rollback was called
        self.mock_unit_of_work.rollback.assert_called_once()

    def test_get_stock_by_symbol_success(self):
        """Should retrieve stock by symbol successfully."""
        # Arrange
        symbol = "AAPL"
        stock_entity = StockEntity(
            symbol=StockSymbol("AAPL"),
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes="Great company",
            stock_id=123,
        )
        self.mock_stock_repository.get_by_symbol.return_value = stock_entity

        # Act
        result = self.service.get_stock_by_symbol(symbol)

        # Assert
        assert isinstance(result, StockDto)
        assert result.id == 123
        assert result.symbol == "AAPL"
        assert result.name == "Apple Inc."
        assert result.industry_group == "Technology"
        assert result.grade == "A"
        assert result.notes == "Great company"

        # Verify repository interaction
        self.mock_stock_repository.get_by_symbol.assert_called_once_with(
            StockSymbol("AAPL")
        )

    def test_get_stock_by_symbol_not_found(self):
        """Should return None when stock not found."""
        # Arrange
        symbol = "NFND"  # Valid 4-character symbol
        self.mock_stock_repository.get_by_symbol.return_value = None

        # Act
        result = self.service.get_stock_by_symbol(symbol)

        # Assert
        assert result is None

        # Verify repository interaction
        self.mock_stock_repository.get_by_symbol.assert_called_once_with(
            StockSymbol("NFND")
        )

    def test_get_all_stocks_success(self):
        """Should retrieve all stocks successfully."""
        # Arrange
        stock1 = StockEntity(symbol=StockSymbol("AAPL"), name="Apple Inc.", stock_id=1)
        stock2 = StockEntity(
            symbol=StockSymbol("MSFT"), name="Microsoft Corp.", stock_id=2
        )

        self.mock_stock_repository.get_all.return_value = [stock1, stock2]

        # Act
        result = self.service.get_all_stocks()

        # Assert
        assert len(result) == 2
        assert all(isinstance(dto, StockDto) for dto in result)
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "MSFT"

        # Verify repository interaction
        self.mock_stock_repository.get_all.assert_called_once()

    def test_get_all_stocks_empty_list(self):
        """Should handle empty stock list."""
        # Arrange
        self.mock_stock_repository.get_all.return_value = []

        # Act
        result = self.service.get_all_stocks()

        # Assert
        assert result == []

        # Verify repository interaction
        self.mock_stock_repository.get_all.assert_called_once()

    def test_update_stock_grade_success(self):
        """Should update stock grade successfully."""
        # Arrange
        symbol = "AAPL"
        new_grade = "A"
        stock_entity = StockEntity(
            symbol=StockSymbol("AAPL"), name="Apple Inc.", grade="B", stock_id=123
        )

        self.mock_stock_repository.get_by_symbol.return_value = stock_entity
        self.mock_stock_repository.update.return_value = True

        # Act
        result = self.service.update_stock_grade(symbol, new_grade)

        # Assert
        assert isinstance(result, StockDto)
        assert result.grade == "A"

        # Verify the entity was updated
        assert stock_entity.grade == "A"

        # Verify repository interactions
        self.mock_stock_repository.get_by_symbol.assert_called_once_with(
            StockSymbol("AAPL")
        )
        self.mock_stock_repository.update.assert_called_once()
        self.mock_unit_of_work.commit.assert_called_once()

    def test_update_stock_grade_not_found(self):
        """Should raise error when trying to update non-existent stock."""
        # Arrange
        symbol = "NFND"  # Valid 4-character symbol
        new_grade = "A"

        self.mock_stock_repository.get_by_symbol.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Stock with symbol NFND not found"):
            self.service.update_stock_grade(symbol, new_grade)

        # Verify no update was attempted
        self.mock_stock_repository.update.assert_not_called()
        self.mock_unit_of_work.commit.assert_not_called()

    def test_stock_exists_true(self):
        """Should return True when stock exists."""
        # Arrange
        symbol = "AAPL"
        self.mock_stock_repository.exists_by_symbol.return_value = True

        # Act
        result = self.service.stock_exists(symbol)

        # Assert
        assert result is True

        # Verify repository interaction
        self.mock_stock_repository.exists_by_symbol.assert_called_once_with(
            StockSymbol("AAPL")
        )

    def test_stock_exists_false(self):
        """Should return False when stock doesn't exist."""
        # Arrange
        symbol = "NFND"  # Valid 4-character symbol
        self.mock_stock_repository.exists_by_symbol.return_value = False

        # Act
        result = self.service.stock_exists(symbol)

        # Assert
        assert result is False

        # Verify repository interaction
        self.mock_stock_repository.exists_by_symbol.assert_called_once_with(
            StockSymbol("NFND")
        )
