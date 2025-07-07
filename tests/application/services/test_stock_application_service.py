"""
Tests for StockApplicationService.

Following TDD approach - these tests define the expected behavior
of the application service that orchestrates stock operations.
"""

from unittest.mock import Mock, patch

import pytest

from src.application.commands.stock import (
    CreateStockCommand,
    CreateStockInputs,
    UpdateStockCommand,
    UpdateStockInputs,
)
from src.application.dto.stock_dto import StockDto
from src.application.services.stock_application_service import StockApplicationService
from src.domain.entities.stock import Stock
from src.domain.repositories.interfaces import IStockBookUnitOfWork, IStockRepository
from src.domain.value_objects import CompanyName, Grade, IndustryGroup, Notes
from src.domain.value_objects.sector import Sector
from src.domain.value_objects.stock_symbol import StockSymbol


class TestStockApplicationService:
    """Test suite for StockApplicationService."""

    def setup_method(self) -> None:
        """Set up test dependencies."""
        self.mock_stock_repository = Mock(spec=IStockRepository)
        self.mock_unit_of_work = Mock(spec=IStockBookUnitOfWork)
        self.mock_unit_of_work.stocks = self.mock_stock_repository

        # Make unit of work support context manager protocol
        self.mock_unit_of_work.__enter__ = Mock(return_value=self.mock_unit_of_work)
        self.mock_unit_of_work.__exit__ = Mock(return_value=None)

        self.service = StockApplicationService(self.mock_unit_of_work)

    def test_create_stock_with_valid_command(self) -> None:
        """Should create stock successfully with valid command."""
        # Arrange
        inputs = CreateStockInputs(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Great company",
        )
        command = CreateStockCommand(inputs)

        # Mock repository to return None (stock doesn't exist)
        self.mock_stock_repository.get_by_symbol.return_value = None

        # Act
        result = self.service.create_stock(command)

        # Assert
        assert isinstance(result, StockDto)
        assert result.id is not None
        assert isinstance(result.id, str)
        assert len(result.id) > 0
        assert result.symbol == "AAPL"
        assert result.name == "Apple Inc."
        assert result.sector == "Technology"
        assert result.industry_group == "Software"
        assert result.grade == "A"
        assert result.notes == "Great company"

        # Verify repository interactions
        self.mock_stock_repository.get_by_symbol.assert_called_once()
        self.mock_stock_repository.create.assert_called_once()
        self.mock_unit_of_work.commit.assert_called_once()

        # Verify the entity passed to repository
        create_call = self.mock_stock_repository.create.call_args[0][0]
        assert isinstance(create_call, Stock)
        assert str(create_call.symbol) == "AAPL"
        assert create_call.company_name is not None
        assert create_call.company_name.value == "Apple Inc."

    def test_create_stock_without_company_name(self) -> None:
        """Should create stock successfully without company name."""
        # Arrange
        inputs = CreateStockInputs(
            symbol="TSLA",
            name=None,  # No company name
            sector="Technology",
            grade="B",
        )
        command = CreateStockCommand(inputs)

        # Mock repository to return None (stock doesn't exist)
        self.mock_stock_repository.get_by_symbol.return_value = None

        # Act
        result = self.service.create_stock(command)

        # Assert
        assert isinstance(result, StockDto)
        assert result.symbol == "TSLA"
        assert result.name is None
        assert result.sector == "Technology"
        assert result.grade == "B"

        # Verify the entity passed to repository
        create_call = self.mock_stock_repository.create.call_args[0][0]
        assert isinstance(create_call, Stock)
        assert str(create_call.symbol) == "TSLA"
        assert create_call.company_name is None

    def test_create_stock_with_duplicate_symbol_raises_error(self) -> None:
        """Should raise error when trying to create stock with existing symbol."""
        # Arrange
        inputs = CreateStockInputs(symbol="AAPL", name="Apple Inc.")
        command = CreateStockCommand(inputs)

        # Mock repository to return existing stock
        existing_stock = (
            Stock.Builder()
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Existing Apple Inc."))
            .with_id("stock-id-456")
            .build()
        )
        self.mock_stock_repository.get_by_symbol.return_value = existing_stock

        # Act & Assert
        with pytest.raises(ValueError, match="Stock with symbol AAPL already exists"):
            _ = self.service.create_stock(command)

        # Verify no creation was attempted
        self.mock_stock_repository.create.assert_not_called()
        self.mock_unit_of_work.commit.assert_not_called()

    def test_create_stock_handles_repository_error(self) -> None:
        """Should handle repository errors gracefully."""
        # Arrange
        inputs = CreateStockInputs(symbol="AAPL", name="Apple Inc.")
        command = CreateStockCommand(inputs)

        self.mock_stock_repository.get_by_symbol.return_value = None
        self.mock_stock_repository.create.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            _ = self.service.create_stock(command)

        # Verify rollback was called
        self.mock_unit_of_work.rollback.assert_called_once()

    def test_get_stock_by_symbol_success(self) -> None:
        """Should retrieve stock by symbol successfully."""
        # Arrange
        symbol = "AAPL"
        stock_entity = (
            Stock.Builder()
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .with_sector(Sector("Technology"))
            .with_industry_group(IndustryGroup("Software"))
            .with_grade(Grade("A"))
            .with_notes(Notes("Great company"))
            .with_id("stock-id-123")
            .build()
        )
        self.mock_stock_repository.get_by_symbol.return_value = stock_entity

        # Act
        result = self.service.get_stock_by_symbol(symbol)

        # Assert
        assert isinstance(result, StockDto)
        assert result.id == "stock-id-123"
        assert result.symbol == "AAPL"
        assert result.name == "Apple Inc."
        assert result.sector == "Technology"
        assert result.industry_group == "Software"
        assert result.grade == "A"
        assert result.notes == "Great company"

        # Verify repository interaction
        self.mock_stock_repository.get_by_symbol.assert_called_once_with(
            StockSymbol("AAPL"),
        )

    def test_get_stock_by_symbol_not_found(self) -> None:
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
            StockSymbol("NFND"),
        )

    def test_get_all_stocks_success(self) -> None:
        """Should retrieve all stocks successfully."""
        # Arrange
        stock1 = (
            Stock.Builder()
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .with_id("stock-1")
            .build()
        )
        stock2 = (
            Stock.Builder()
            .with_symbol(StockSymbol("MSFT"))
            .with_company_name(CompanyName("Microsoft Corp."))
            .with_id("stock-2")
            .build()
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

    def test_get_all_stocks_empty_list(self) -> None:
        """Should handle empty stock list."""
        # Arrange
        self.mock_stock_repository.get_all.return_value = []

        # Act
        result = self.service.get_all_stocks()

        # Assert
        assert result == []

        # Verify repository interaction
        self.mock_stock_repository.get_all.assert_called_once()

    def test_stock_exists_true(self) -> None:
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
            StockSymbol("AAPL"),
        )

    def test_stock_exists_false(self) -> None:
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
            StockSymbol("NFND"),
        )

    def test_search_stocks_with_filters(self) -> None:
        """Should search stocks with filter criteria."""
        # Arrange
        symbol_filter = "APP"
        name_filter = "Apple"
        industry_filter = "Tech"

        mock_entities = [
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .with_sector(Sector("Technology"))
            .with_industry_group(IndustryGroup("Software"))
            .with_grade(Grade("A"))
            .with_notes(Notes(""))
            .build(),
        ]
        self.mock_stock_repository.search_stocks.return_value = mock_entities

        # Act
        result = self.service.search_stocks(
            symbol_filter=symbol_filter,
            name_filter=name_filter,
            industry_filter=industry_filter,
        )

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], StockDto)
        assert result[0].symbol == "AAPL"
        assert result[0].name == "Apple Inc."

        self.mock_stock_repository.search_stocks.assert_called_once_with(
            symbol_filter=symbol_filter,
            name_filter=name_filter,
            industry_filter=industry_filter,
        )

    def test_search_stocks_no_filters(self) -> None:
        """Should search stocks without any filters."""
        # Arrange
        mock_entities = [
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .with_sector(Sector("Technology"))
            .with_industry_group(IndustryGroup("Software"))
            .with_grade(Grade("A"))
            .with_notes(Notes(""))
            .build(),
            Stock.Builder()
            .with_id("stock-2")
            .with_symbol(StockSymbol("GOOGL"))
            .with_company_name(CompanyName("Alphabet Inc."))
            .with_sector(Sector("Technology"))
            .with_industry_group(IndustryGroup("Software"))
            .with_grade(Grade("A"))
            .with_notes(Notes(""))
            .build(),
        ]
        self.mock_stock_repository.search_stocks.return_value = mock_entities

        # Act
        result = self.service.search_stocks()

        # Assert
        assert len(result) == 2
        assert all(isinstance(dto, StockDto) for dto in result)

        self.mock_stock_repository.search_stocks.assert_called_once_with(
            symbol_filter=None,
            name_filter=None,
            industry_filter=None,
        )

    def test_search_stocks_empty_results(self) -> None:
        """Should handle empty search results gracefully."""
        # Arrange
        symbol_filter = "NOTFOUND"
        self.mock_stock_repository.search_stocks.return_value = []

        # Act
        result = self.service.search_stocks(symbol_filter=symbol_filter)

        # Assert
        assert len(result) == 0
        assert isinstance(result, list)

        self.mock_stock_repository.search_stocks.assert_called_once_with(
            symbol_filter=symbol_filter,
            name_filter=None,
            industry_filter=None,
        )

    def test_update_stock_with_valid_command(self) -> None:
        """Should update stock successfully with valid command."""
        # Arrange
        inputs = UpdateStockInputs(
            stock_id="stock-1",
            name="Apple Inc. (Updated)",
            sector="Technology",
            industry_group="Hardware",
            grade="A",
            notes="Updated notes",
        )
        command = UpdateStockCommand(inputs)

        existing_stock = (
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .with_sector(Sector("Technology"))
            .with_industry_group(IndustryGroup("Software"))
            .with_grade(Grade("B"))
            .with_notes(Notes("Old notes"))
            .build()
        )

        # Mock repository responses
        self.mock_stock_repository.get_by_id.return_value = existing_stock
        self.mock_stock_repository.update.return_value = True

        # Act
        result = self.service.update_stock(command)

        # Assert
        assert isinstance(result, StockDto)
        assert result.id == "stock-1"
        assert result.name == "Apple Inc. (Updated)"
        assert result.sector == "Technology"
        assert result.industry_group == "Hardware"
        assert result.grade == "A"
        assert result.notes == "Updated notes"

        # Verify repository interactions
        self.mock_stock_repository.get_by_id.assert_called_once_with("stock-1")
        self.mock_stock_repository.update.assert_called_once()
        self.mock_unit_of_work.commit.assert_called_once()

    def test_update_stock_with_partial_command(self) -> None:
        """Should update only specified fields."""
        # Arrange
        inputs = UpdateStockInputs(
            stock_id="stock-1",
            grade="A",  # Only updating grade
        )
        command = UpdateStockCommand(inputs)

        existing_stock = (
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .with_sector(Sector("Technology"))
            .with_industry_group(IndustryGroup("Software"))
            .with_grade(Grade("B"))
            .with_notes(Notes("Existing notes"))
            .build()
        )

        # Mock repository responses
        self.mock_stock_repository.get_by_id.return_value = existing_stock
        self.mock_stock_repository.update.return_value = True

        # Act
        result = self.service.update_stock(command)

        # Assert
        assert isinstance(result, StockDto)
        assert result.grade == "A"
        # Verify other fields remain unchanged
        assert result.name == "Apple Inc."
        assert result.sector == "Technology"
        assert result.industry_group == "Software"
        assert result.notes == "Existing notes"

    def test_update_stock_with_nonexistent_stock_raises_error(self) -> None:
        """Should raise error when stock doesn't exist."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-999", grade="A")
        command = UpdateStockCommand(inputs)
        self.mock_stock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Stock with ID stock-999 not found"):
            _ = self.service.update_stock(command)

        # Verify rollback was called
        self.mock_unit_of_work.rollback.assert_called_once()

    def test_update_stock_with_empty_command_raises_error(self) -> None:
        """Should raise error when no fields to update."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-1")
        command = UpdateStockCommand(inputs)  # No fields to update

        # Act & Assert
        with pytest.raises(ValueError, match="No fields to update"):
            _ = self.service.update_stock(command)

    def test_update_stock_with_repository_failure_raises_error(self) -> None:
        """Should handle repository update failure."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-1", grade="A")
        command = UpdateStockCommand(inputs)

        existing_stock = (
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .with_grade(Grade("B"))
            .build()
        )

        self.mock_stock_repository.get_by_id.return_value = existing_stock
        self.mock_stock_repository.update.return_value = False  # Simulate failure

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to update stock"):
            _ = self.service.update_stock(command)

        # Verify rollback was called
        self.mock_unit_of_work.rollback.assert_called_once()

    def test_update_stock_with_exception_rolls_back_transaction(self) -> None:
        """Should rollback transaction on any exception."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-1", grade="A")
        command = UpdateStockCommand(inputs)

        existing_stock = (
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .with_grade(Grade("B"))
            .build()
        )

        self.mock_stock_repository.get_by_id.return_value = existing_stock
        self.mock_stock_repository.update.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            _ = self.service.update_stock(command)

        # Verify rollback was called
        self.mock_unit_of_work.rollback.assert_called_once()

    def test_update_stock_with_duplicate_symbol_raises_error(self) -> None:
        """Should raise error when changing to an existing symbol."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-1", symbol="MSFT")
        command = UpdateStockCommand(inputs)

        existing_stock = (
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .build()
        )

        # Another stock with the target symbol already exists
        another_stock = (
            Stock.Builder()
            .with_id("stock-2")
            .with_symbol(StockSymbol("MSFT"))
            .with_company_name(CompanyName("Microsoft Corporation"))
            .build()
        )

        self.mock_stock_repository.get_by_id.return_value = existing_stock
        self.mock_stock_repository.get_by_symbol.return_value = another_stock

        # Act & Assert
        with pytest.raises(ValueError, match="Stock with symbol MSFT already exists"):
            _ = self.service.update_stock(command)

        # Verify rollback was called
        self.mock_unit_of_work.rollback.assert_called_once()

    def test_update_stock_with_same_symbol_allowed(self) -> None:
        """Should allow updating stock with same symbol (no change)."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-1", symbol="AAPL", grade="A")
        command = UpdateStockCommand(inputs)

        existing_stock = (
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .with_grade(Grade("B"))
            .build()
        )

        self.mock_stock_repository.get_by_id.return_value = existing_stock
        self.mock_stock_repository.update.return_value = True

        # Act
        result = self.service.update_stock(command)

        # Assert
        assert result.id == "stock-1"
        assert result.symbol == "AAPL"
        assert result.grade == "A"

        # Verify get_by_symbol was NOT called since symbol didn't change
        self.mock_stock_repository.get_by_symbol.assert_not_called()

    def test_update_stock_changing_symbol_to_available_one(self) -> None:
        """Should allow changing symbol when new symbol is available."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-1", symbol="APLE")
        command = UpdateStockCommand(inputs)

        existing_stock = (
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .build()
        )

        self.mock_stock_repository.get_by_id.return_value = existing_stock
        self.mock_stock_repository.get_by_symbol.return_value = (
            None  # No existing stock with new symbol
        )
        self.mock_stock_repository.update.return_value = True

        # Act
        result = self.service.update_stock(command)

        # Assert
        assert result.id == "stock-1"
        assert result.symbol == "APLE"

        # Verify symbol check was performed
        self.mock_stock_repository.get_by_symbol.assert_called_once()

    def test_create_stock_with_value_object_creation_error(self) -> None:
        """Should handle errors during value object creation."""
        # Arrange
        inputs = CreateStockInputs(symbol="AAPL", name="Apple Inc.")
        command = CreateStockCommand(inputs)

        # Mock repository to return None (stock doesn't exist)
        self.mock_stock_repository.get_by_symbol.return_value = None

        # Mock StockSymbol to raise an error during creation
        with patch(
            "src.application.services.stock_application_service.StockSymbol",
        ) as mock_symbol_class:
            mock_symbol_class.side_effect = ValueError("Invalid symbol format")

            # Act & Assert
            with pytest.raises(ValueError, match="Invalid symbol format"):
                _ = self.service.create_stock(command)

            # Verify rollback was called
            self.mock_unit_of_work.rollback.assert_called_once()

    def test_create_stock_with_context_manager_exit_exception(self) -> None:
        """Should handle exceptions in context manager exit."""
        # Arrange
        inputs = CreateStockInputs(symbol="AAPL", name="Apple Inc.")
        command = CreateStockCommand(inputs)

        # Mock repository to return None (stock doesn't exist)
        self.mock_stock_repository.get_by_symbol.return_value = None

        # Mock __exit__ to raise an exception
        self.mock_unit_of_work.__exit__.side_effect = Exception("Context manager error")

        # Act & Assert
        with pytest.raises(Exception, match="Context manager error"):
            _ = self.service.create_stock(command)

    def test_update_stock_validates_and_retrieves_stock(self) -> None:
        """Should validate command and retrieve stock through update_stock."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-1", name="Updated Apple Inc.")
        command = UpdateStockCommand(inputs)
        stock_entity = (
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .build()
        )

        self.mock_stock_repository.get_by_id.return_value = stock_entity
        self.mock_stock_repository.update.return_value = True

        # Act
        result = self.service.update_stock(command)

        # Assert
        assert result.id == "stock-1"
        assert result.name == "Updated Apple Inc."
        self.mock_stock_repository.get_by_id.assert_called_once_with("stock-1")

    def test_update_stock_raises_when_stock_not_found(self) -> None:
        """Should raise error when stock not found through update_stock."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-999", name="Apple Inc.")
        command = UpdateStockCommand(inputs)
        self.mock_stock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Stock with ID stock-999 not found"):
            _ = self.service.update_stock(command)

    def test_update_stock_raises_when_no_fields_to_update(self) -> None:
        """Should raise error when no fields to update through update_stock."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-1")
        command = UpdateStockCommand(inputs)  # No fields to update

        # Act & Assert
        with pytest.raises(ValueError, match="No fields to update"):
            _ = self.service.update_stock(command)

    def test_update_stock_applies_updates_and_saves(self) -> None:
        """Should apply updates and save through update_stock."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-1", name="Updated Apple Inc.")
        command = UpdateStockCommand(inputs)
        stock_entity = (
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .build()
        )

        self.mock_stock_repository.get_by_id.return_value = stock_entity
        self.mock_stock_repository.update.return_value = True

        # Act
        result = self.service.update_stock(command)

        # Assert
        assert result.name == "Updated Apple Inc."
        self.mock_stock_repository.update.assert_called_once_with(
            "stock-1",
            stock_entity,
        )

    def test_update_stock_raises_when_repository_update_fails(self) -> None:
        """Should raise error when repository update fails through update_stock."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-1", name="Updated Apple Inc.")
        command = UpdateStockCommand(inputs)
        stock_entity = (
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .build()
        )

        self.mock_stock_repository.get_by_id.return_value = stock_entity
        self.mock_stock_repository.update.return_value = False  # Simulate failure

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to update stock"):
            _ = self.service.update_stock(command)

    def test_get_stock_by_symbol_with_invalid_symbol_format(self) -> None:
        """Should handle invalid symbol format in get_stock_by_symbol."""
        # This tests the case where StockSymbol creation might fail
        with patch(
            "src.application.services.stock_application_service.StockSymbol",
        ) as mock_symbol_class:
            mock_symbol_class.side_effect = ValueError("Invalid symbol format")

            # Act & Assert
            with pytest.raises(ValueError, match="Invalid symbol format"):
                _ = self.service.get_stock_by_symbol("INVALID")

    def test_stock_exists_with_invalid_symbol_format(self) -> None:
        """Should handle invalid symbol format in stock_exists."""
        # This tests the case where StockSymbol creation might fail
        with patch(
            "src.application.services.stock_application_service.StockSymbol",
        ) as mock_symbol_class:
            mock_symbol_class.side_effect = ValueError("Invalid symbol format")

            # Act & Assert
            with pytest.raises(ValueError, match="Invalid symbol format"):
                _ = self.service.stock_exists("INVALID")

    def test_search_stocks_with_repository_error(self) -> None:
        """Should handle repository errors in search_stocks."""
        # Arrange
        self.mock_stock_repository.search_stocks.side_effect = Exception(
            "Database error",
        )

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            _ = self.service.search_stocks(symbol_filter="AAPL")

    def test_get_all_stocks_with_repository_error(self) -> None:
        """Should handle repository errors in get_all_stocks."""
        # Arrange
        self.mock_stock_repository.get_all.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            _ = self.service.get_all_stocks()

    def test_create_stock_with_commit_failure(self) -> None:
        """Should handle commit failure in create_stock."""
        # Arrange
        inputs = CreateStockInputs(symbol="AAPL", name="Apple Inc.")
        command = CreateStockCommand(inputs)
        self.mock_stock_repository.get_by_symbol.return_value = None

        # Mock commit to fail
        self.mock_unit_of_work.commit.side_effect = Exception("Commit failed")

        # Act & Assert
        with pytest.raises(Exception, match="Commit failed"):
            _ = self.service.create_stock(command)

        # Verify rollback was called
        self.mock_unit_of_work.rollback.assert_called_once()

    def test_update_stock_with_commit_failure(self) -> None:
        """Should handle commit failure in update_stock."""
        # Arrange
        inputs = UpdateStockInputs(stock_id="stock-1", name="Updated Apple Inc.")
        command = UpdateStockCommand(inputs)
        stock_entity = (
            Stock.Builder()
            .with_id("stock-1")
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .build()
        )

        self.mock_stock_repository.get_by_id.return_value = stock_entity
        self.mock_stock_repository.update.return_value = True

        # Mock the update_fields method on the entity
        stock_entity.update_fields = Mock()

        # Mock commit to fail
        self.mock_unit_of_work.commit.side_effect = Exception("Commit failed")

        # Act & Assert
        with pytest.raises(Exception, match="Commit failed"):
            _ = self.service.update_stock(command)

        # Verify rollback was called
        self.mock_unit_of_work.rollback.assert_called_once()

    def test_get_stock_by_id_success(self) -> None:
        """Should retrieve stock by ID successfully."""
        # Arrange
        stock_id = "stock-id-123"
        stock_entity = (
            Stock.Builder()
            .with_symbol(StockSymbol("AAPL"))
            .with_company_name(CompanyName("Apple Inc."))
            .with_sector(Sector("Technology"))
            .with_industry_group(IndustryGroup("Software"))
            .with_grade(Grade("A"))
            .with_notes(Notes("Great company"))
            .with_id("stock-id-123")
            .build()
        )
        self.mock_stock_repository.get_by_id.return_value = stock_entity

        # Act
        result = self.service.get_stock_by_id(stock_id)

        # Assert
        assert isinstance(result, StockDto)
        assert result.id == "stock-id-123"
        assert result.symbol == "AAPL"
        assert result.name == "Apple Inc."
        assert result.sector == "Technology"
        assert result.industry_group == "Software"
        assert result.grade == "A"
        assert result.notes == "Great company"

        # Verify repository interaction
        self.mock_stock_repository.get_by_id.assert_called_once_with(stock_id)

    def test_get_stock_by_id_not_found(self) -> None:
        """Should return None when stock not found by ID."""
        # Arrange
        stock_id = "non-existent-id"
        self.mock_stock_repository.get_by_id.return_value = None

        # Act
        result = self.service.get_stock_by_id(stock_id)

        # Assert
        assert result is None

        # Verify repository interaction
        self.mock_stock_repository.get_by_id.assert_called_once_with(stock_id)

    def test_get_stock_by_id_with_repository_error(self) -> None:
        """Should handle repository errors in get_stock_by_id."""
        # Arrange
        stock_id = "stock-id-123"
        self.mock_stock_repository.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            _ = self.service.get_stock_by_id(stock_id)
