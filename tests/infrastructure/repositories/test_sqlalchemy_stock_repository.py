"""
Unit tests for SqlAlchemyStockRepository.

This module tests the SQLAlchemy Core implementation of the stock repository,
following TDD principles to define expected behavior before implementation.
"""

# pyright: reportPrivateUsage=false, reportUnknownArgumentType=false
# pyright: reportUnusedImport=false, reportUnusedCallResult=false

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from sqlalchemy import exc

from src.domain.entities.stock import Stock
from src.domain.repositories.interfaces import IStockRepository
from src.domain.value_objects import (
    CompanyName,
    Grade,
    IndustryGroup,
    Notes,
    Sector,
    StockSymbol,
)
from src.infrastructure.persistence.interfaces import IDatabaseConnection
from src.infrastructure.persistence.tables.stock_table import stock_table
from src.infrastructure.repositories.sqlalchemy_stock_repository import (
    SqlAlchemyStockRepository,
)


class TestSqlAlchemyStockRepositoryConstruction:
    """Test repository construction and initialization."""

    def test_repository_accepts_database_connection(self) -> None:
        """Should accept IDatabaseConnection in constructor."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)

        # Act
        repository = SqlAlchemyStockRepository(mock_connection)

        # Assert
        assert isinstance(repository, IStockRepository)
        assert repository._connection is mock_connection

    def test_repository_implements_istockrepository_interface(self) -> None:
        """Should implement all methods from IStockRepository interface."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        repository = SqlAlchemyStockRepository(mock_connection)

        # Assert - Check all required methods exist
        assert hasattr(repository, "create")
        assert hasattr(repository, "get_by_id")
        assert hasattr(repository, "get_by_symbol")
        assert hasattr(repository, "get_all")
        assert hasattr(repository, "update")
        assert hasattr(repository, "delete")
        assert hasattr(repository, "exists_by_symbol")
        assert hasattr(repository, "search_stocks")


class TestSqlAlchemyStockRepositoryCreate:
    """Test the create method of the repository."""

    def test_create_inserts_stock_with_all_fields(self) -> None:
        """Should successfully insert a stock with all fields populated."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        stock = Stock(
            id="test-stock-123",
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
            sector=Sector("Technology"),
            industry_group=IndustryGroup("Software"),
            grade=Grade("A"),
            notes=Notes("Leading tech company"),
        )

        # Act
        result_id = repository.create(stock)

        # Assert
        assert result_id == "test-stock-123"

        # Verify the insert statement was called
        mock_connection.execute.assert_called_once()
        call_args = mock_connection.execute.call_args
        statement = call_args[0][0]

        # Verify it's an insert statement for the stocks table
        assert statement.is_insert
        assert statement.table.name == "stocks"

        # Verify the values being inserted by checking the compiled statement
        # SQLAlchemy Core statements store values internally, not as 'parameters'
        compiled = statement.compile()
        params = compiled.params
        assert params["id"] == "test-stock-123"
        assert params["symbol"] == "AAPL"
        assert params["company_name"] == "Apple Inc."
        assert params["sector"] == "Technology"
        assert params["industry_group"] == "Software"
        assert params["grade"] == "A"
        assert params["notes"] == "Leading tech company"
        assert "created_at" in params
        assert "updated_at" in params

    def test_create_inserts_stock_with_minimal_fields(self) -> None:
        """Should successfully insert a stock with only required fields."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        stock = Stock(
            symbol=StockSymbol("MSFT"),
            company_name=CompanyName("Microsoft Corporation"),
        )

        # Act
        result_id = repository.create(stock)

        # Assert
        assert result_id is not None
        assert isinstance(result_id, str)

        # Verify the insert statement
        call_args = mock_connection.execute.call_args
        statement = call_args[0][0]
        compiled = statement.compile()
        params = compiled.params

        assert params["symbol"] == "MSFT"
        assert params["company_name"] == "Microsoft Corporation"
        assert params["sector"] is None
        assert params["industry_group"] is None
        assert params["grade"] is None
        assert params["notes"] == ""  # Empty notes

    def test_create_inserts_stock_without_company_name(self) -> None:
        """Should successfully insert a stock without company name."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        stock = Stock(
            symbol=StockSymbol("GOOGL"),
            company_name=None,  # No company name
        )

        # Act
        result_id = repository.create(stock)

        # Assert
        assert result_id is not None
        assert isinstance(result_id, str)

        # Verify the insert statement
        call_args = mock_connection.execute.call_args
        statement = call_args[0][0]
        compiled = statement.compile()
        params = compiled.params

        assert params["symbol"] == "GOOGL"
        assert params["company_name"] is None  # Should be None
        assert params["sector"] is None
        assert params["industry_group"] is None
        assert params["grade"] is None
        assert params["notes"] == ""  # Empty notes

    def test_create_uses_entity_id_when_no_id_provided(self) -> None:
        """Should use the ID already generated by the entity when no ID is provided."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Create stock without ID - Entity base class will generate one
        stock = Stock(
            symbol=StockSymbol("GOOGL"),
            company_name=CompanyName("Alphabet Inc."),
        )

        # Store the entity's generated ID
        entity_generated_id = stock.id

        # Act
        result_id = repository.create(stock)

        # Assert
        assert result_id == entity_generated_id
        assert result_id is not None
        assert len(result_id) == 36  # UUID format

        # Verify the entity's ID was used in the insert
        call_args = mock_connection.execute.call_args
        statement = call_args[0][0]
        compiled = statement.compile()
        params = compiled.params
        assert params["id"] == entity_generated_id

    def test_create_handles_duplicate_symbol_constraint(self) -> None:
        """Should handle duplicate symbol constraint violation gracefully."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_connection.execute.side_effect = exc.IntegrityError(
            "UNIQUE constraint failed: stocks.symbol", params={}, orig=None
        )

        repository = SqlAlchemyStockRepository(mock_connection)

        stock = Stock(
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Stock with symbol AAPL already exists"):
            repository.create(stock)

    def test_create_propagates_other_database_errors(self) -> None:
        """Should propagate non-constraint database errors."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_connection.execute.side_effect = exc.DatabaseError(
            "Database connection lost", params={}, orig=None
        )

        repository = SqlAlchemyStockRepository(mock_connection)

        stock = Stock(
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
        )

        # Act & Assert
        with pytest.raises(exc.DatabaseError):
            repository.create(stock)


class TestSqlAlchemyStockRepositoryGetBySymbol:
    """Test the get_by_symbol method of the repository."""

    def test_get_by_symbol_returns_stock_when_found(self) -> None:
        """Should return Stock entity when symbol exists in database."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()

        # Mock the database row
        mock_row = {
            "id": "stock-123",
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "sector": "Technology",
            "industry_group": "Software",
            "grade": "A",
            "notes": "Tech giant",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        mock_result.fetchone.return_value = mock_row
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)
        symbol = StockSymbol("AAPL")

        # Act
        result = repository.get_by_symbol(symbol)

        # Assert
        assert result is not None
        assert isinstance(result, Stock)
        assert result.id == "stock-123"
        assert result.symbol.value == "AAPL"
        assert result.company_name is not None
        assert result.company_name.value == "Apple Inc."
        assert result.sector is not None
        assert result.sector.value == "Technology"
        assert result.industry_group is not None
        assert result.industry_group.value == "Software"
        assert result.grade is not None
        assert result.grade.value == "A"
        assert result.notes.value == "Tech giant"

        # Verify the select statement
        call_args = mock_connection.execute.call_args
        statement = call_args[0][0]
        assert statement.is_select
        # Use get_final_froms() instead of deprecated froms attribute
        froms = statement.get_final_froms()
        assert len(froms) > 0
        assert froms[0].name == "stocks"

    def test_get_by_symbol_returns_none_when_not_found(self) -> None:
        """Should return None when symbol does not exist in database."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)
        symbol = StockSymbol("NONE")

        # Act
        result = repository.get_by_symbol(symbol)

        # Assert
        assert result is None

    def test_get_by_symbol_handles_null_optional_fields(self) -> None:
        """Should correctly map null database fields to None in entity."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()

        # Mock row with null optional fields
        mock_row = {
            "id": "stock-456",
            "symbol": "MIN",
            "company_name": "Minimal Corp",
            "sector": None,
            "industry_group": None,
            "grade": None,
            "notes": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        mock_result.fetchone.return_value = mock_row
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)
        symbol = StockSymbol("MIN")

        # Act
        result = repository.get_by_symbol(symbol)

        # Assert
        assert result is not None
        assert result.sector is None
        assert result.industry_group is None
        assert result.grade is None
        assert result.notes.value == ""  # Empty notes, not None

    def test_get_by_symbol_handles_null_company_name(self) -> None:
        """Should correctly handle null company name from database."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()

        # Mock row with null company name
        mock_row = {
            "id": "stock-789",
            "symbol": "TEST",
            "company_name": None,  # No company name
            "sector": "Technology",
            "industry_group": "Software",
            "grade": "B",
            "notes": "Test stock",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        mock_result.fetchone.return_value = mock_row
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)
        symbol = StockSymbol("TEST")

        # Act
        result = repository.get_by_symbol(symbol)

        # Assert
        assert result is not None
        assert result.company_name is None
        assert result.symbol.value == "TEST"
        assert result.sector is not None
        assert result.sector.value == "Technology"


class TestSqlAlchemyStockRepositoryHelperMethods:
    """Test the helper methods for entity-row mapping."""

    def test_entity_to_row_maps_all_fields(self) -> None:
        """Should correctly map Stock entity to database row dict."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        repository = SqlAlchemyStockRepository(mock_connection)

        stock = Stock(
            id="test-123",
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
            sector=Sector("Technology"),
            industry_group=IndustryGroup("Software"),
            grade=Grade("A"),
            notes=Notes("Test notes"),
        )

        # Act
        row_dict = repository._entity_to_row(stock)

        # Assert
        assert row_dict["id"] == "test-123"
        assert row_dict["symbol"] == "AAPL"
        assert row_dict["company_name"] == "Apple Inc."
        assert row_dict["sector"] == "Technology"
        assert row_dict["industry_group"] == "Software"
        assert row_dict["grade"] == "A"
        assert row_dict["notes"] == "Test notes"
        assert "created_at" in row_dict
        assert "updated_at" in row_dict

    def test_entity_to_row_handles_none_company_name(self) -> None:
        """Should correctly map Stock entity with None company name to row."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        repository = SqlAlchemyStockRepository(mock_connection)

        stock = Stock(
            id="test-456",
            symbol=StockSymbol("XYZ"),
            company_name=None,  # No company name
            sector=Sector("Healthcare"),
            grade=Grade("B"),
        )

        # Act
        row_dict = repository._entity_to_row(stock)

        # Assert
        assert row_dict["id"] == "test-456"
        assert row_dict["symbol"] == "XYZ"
        assert row_dict["company_name"] is None  # Should be None
        assert row_dict["sector"] == "Healthcare"
        assert row_dict["industry_group"] is None
        assert row_dict["grade"] == "B"
        assert row_dict["notes"] == ""

    def test_row_to_entity_maps_all_fields(self) -> None:
        """Should correctly map database row to Stock entity."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        repository = SqlAlchemyStockRepository(mock_connection)

        row = {
            "id": "db-123",
            "symbol": "MSFT",
            "company_name": "Microsoft Corporation",
            "sector": "Technology",
            "industry_group": "Software",
            "grade": "A",
            "notes": "Database notes",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        # Act
        entity = repository._row_to_entity(row)

        # Assert
        assert entity.id == "db-123"
        assert entity.symbol.value == "MSFT"
        assert entity.company_name is not None
        assert entity.company_name.value == "Microsoft Corporation"
        assert entity.sector is not None
        assert entity.sector.value == "Technology"
        assert entity.industry_group is not None
        assert entity.industry_group.value == "Software"
        assert entity.grade is not None
        assert entity.grade.value == "A"
        assert entity.notes.value == "Database notes"


class TestSqlAlchemyStockRepositoryGetById:
    """Test the get_by_id method of the repository."""

    def test_get_by_id_returns_stock_when_found(self) -> None:
        """Should return Stock entity when ID exists in database."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()

        # Mock the database row
        mock_row = {
            "id": "stock-789",
            "symbol": "GOOGL",
            "company_name": "Alphabet Inc.",
            "sector": "Technology",
            "industry_group": "Internet Services",
            "grade": "A",
            "notes": "Parent of Google",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        mock_result.fetchone.return_value = mock_row
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.get_by_id("stock-789")

        # Assert
        assert result is not None
        assert isinstance(result, Stock)
        assert result.id == "stock-789"
        assert result.symbol.value == "GOOGL"
        assert result.company_name is not None
        assert result.company_name.value == "Alphabet Inc."
        assert result.sector is not None
        assert result.sector.value == "Technology"
        assert result.industry_group is not None
        assert result.industry_group.value == "Internet Services"
        assert result.grade is not None
        assert result.grade.value == "A"
        assert result.notes.value == "Parent of Google"

        # Verify the select statement
        call_args = mock_connection.execute.call_args
        statement = call_args[0][0]
        assert statement.is_select
        # Verify it's querying the stocks table
        froms = statement.get_final_froms()
        assert len(froms) > 0
        assert froms[0].name == "stocks"

    def test_get_by_id_returns_none_when_not_found(self) -> None:
        """Should return None when ID does not exist in database."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.get_by_id("non-existent-id")

        # Assert
        assert result is None

    def test_get_by_id_handles_database_errors(self) -> None:
        """Should propagate database errors."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_connection.execute.side_effect = exc.DatabaseError(
            "Database connection lost", params={}, orig=None
        )

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act & Assert
        with pytest.raises(exc.DatabaseError):
            repository.get_by_id("test-id")


class TestSqlAlchemyStockRepositoryGetAll:
    """Test the get_all method of the repository."""

    def test_get_all_returns_empty_list_when_no_stocks(self) -> None:
        """Should return empty list when no stocks exist in database."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.get_all()

        # Assert
        assert result == []
        assert isinstance(result, list)

        # Verify the select statement
        call_args = mock_connection.execute.call_args
        statement = call_args[0][0]
        assert statement.is_select
        froms = statement.get_final_froms()
        assert len(froms) > 0
        assert froms[0].name == "stocks"

    def test_get_all_returns_all_stocks(self) -> None:
        """Should return list of all stocks from database."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()

        # Mock multiple database rows
        mock_rows = [
            {
                "id": "stock-1",
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry_group": "Hardware",
                "grade": "A",
                "notes": "iPhone maker",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": "stock-2",
                "symbol": "MSFT",
                "company_name": "Microsoft Corporation",
                "sector": "Technology",
                "industry_group": "Software",
                "grade": "B",
                "notes": "",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": "stock-3",
                "symbol": "JPM",
                "company_name": "JPMorgan Chase",
                "sector": "Financial Services",
                "industry_group": "Banks",
                "grade": None,
                "notes": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ]

        mock_result.fetchall.return_value = mock_rows
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.get_all()

        # Assert
        assert len(result) == 3
        assert all(isinstance(stock, Stock) for stock in result)

        # Verify first stock
        assert result[0].id == "stock-1"
        assert result[0].symbol.value == "AAPL"
        assert result[0].company_name is not None
        assert result[0].company_name.value == "Apple Inc."
        assert result[0].sector is not None
        assert result[0].sector.value == "Technology"
        assert result[0].grade is not None
        assert result[0].grade.value == "A"

        # Verify second stock
        assert result[1].id == "stock-2"
        assert result[1].symbol.value == "MSFT"
        assert result[1].grade is not None
        assert result[1].grade.value == "B"

        # Verify third stock (with null fields)
        assert result[2].id == "stock-3"
        assert result[2].symbol.value == "JPM"
        assert result[2].grade is None
        assert result[2].notes.value == ""

    def test_get_all_handles_database_errors(self) -> None:
        """Should propagate database errors."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_connection.execute.side_effect = exc.DatabaseError(
            "Database connection lost", params={}, orig=None
        )

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act & Assert
        with pytest.raises(exc.DatabaseError):
            repository.get_all()


class TestSqlAlchemyStockRepositoryUpdate:
    """Test the update method of the repository."""

    def test_update_successfully_updates_existing_stock(self) -> None:
        """Should successfully update stock and return True."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        updated_stock = Stock(
            id="stock-999",
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc. Updated"),
            sector=Sector("Technology"),
            industry_group=IndustryGroup("Hardware"),
            grade=Grade("B"),  # Changed from A to B
            notes=Notes("Updated notes"),
        )

        # Act
        result = repository.update("stock-999", updated_stock)

        # Assert
        assert result is True

        # Verify the update statement
        call_args = mock_connection.execute.call_args
        statement = call_args[0][0]
        assert statement.is_update

        # Verify it's updating the stocks table
        assert statement.table.name == "stocks"

        # Verify the values being updated
        compiled = statement.compile()
        params = compiled.params
        assert params["company_name"] == "Apple Inc. Updated"
        assert params["grade"] == "B"
        assert params["notes"] == "Updated notes"
        assert "updated_at" in params

    def test_update_returns_false_when_stock_not_found(self) -> None:
        """Should return False when trying to update non-existent stock."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_result.rowcount = 0  # No rows affected
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        updated_stock = Stock(
            symbol=StockSymbol("NONE"),
            company_name=CompanyName("Nonexistent Company"),
        )

        # Act
        result = repository.update("non-existent-id", updated_stock)

        # Assert
        assert result is False

    def test_update_uses_stock_id_parameter_not_entity_id(self) -> None:
        """Should use the stock_id parameter for WHERE clause, not entity.id."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Stock with different ID than the one we're updating
        updated_stock = Stock(
            id="different-id",
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
        )

        # Act
        repository.update("target-id", updated_stock)

        # Assert - verify WHERE clause uses parameter, not entity ID
        call_args = mock_connection.execute.call_args
        statement = call_args[0][0]

        # The WHERE clause should filter by the stock_id parameter
        where_clauses = statement.whereclause
        assert where_clauses is not None

    def test_update_handles_database_errors(self) -> None:
        """Should propagate database errors."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_connection.execute.side_effect = exc.DatabaseError(
            "Database connection lost", params={}, orig=None
        )

        repository = SqlAlchemyStockRepository(mock_connection)

        stock = Stock(
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
        )

        # Act & Assert
        with pytest.raises(exc.DatabaseError):
            repository.update("test-id", stock)

    def test_update_handles_constraint_violations(self) -> None:
        """Should handle constraint violations like duplicate symbols."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_connection.execute.side_effect = exc.IntegrityError(
            "UNIQUE constraint failed: stocks.symbol", params={}, orig=None
        )

        repository = SqlAlchemyStockRepository(mock_connection)

        stock = Stock(
            symbol=StockSymbol("MSFT"),  # Trying to change to existing symbol
            company_name=CompanyName("Apple Inc."),
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Stock with symbol MSFT already exists"):
            repository.update("test-id", stock)


class TestSqlAlchemyStockRepositoryDelete:
    """Test the delete method of the repository."""

    def test_delete_successfully_deletes_existing_stock(self) -> None:
        """Should successfully delete stock and return True."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_result.rowcount = 1  # One row deleted
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.delete("stock-to-delete")

        # Assert
        assert result is True

        # Verify the delete statement
        call_args = mock_connection.execute.call_args
        statement = call_args[0][0]
        assert statement.is_delete

        # Verify it's deleting from the stocks table
        assert statement.table.name == "stocks"

        # Verify WHERE clause is present
        assert statement.whereclause is not None

    def test_delete_returns_false_when_stock_not_found(self) -> None:
        """Should return False when trying to delete non-existent stock."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_result.rowcount = 0  # No rows deleted
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.delete("non-existent-id")

        # Assert
        assert result is False

    def test_delete_handles_database_errors(self) -> None:
        """Should propagate database errors."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_connection.execute.side_effect = exc.DatabaseError(
            "Database connection lost", params={}, orig=None
        )

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act & Assert
        with pytest.raises(exc.DatabaseError):
            repository.delete("test-id")

    def test_delete_handles_foreign_key_constraints(self) -> None:
        """Should handle foreign key constraint violations gracefully."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_connection.execute.side_effect = exc.IntegrityError(
            "FOREIGN KEY constraint failed", params={}, orig=None
        )

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act & Assert
        with pytest.raises(exc.IntegrityError):
            repository.delete("stock-with-references")


class TestSqlAlchemyStockRepositoryExistsBySymbol:
    """Test the exists_by_symbol method of the repository."""

    def test_exists_by_symbol_returns_true_when_stock_exists(self) -> None:
        """Should return True when stock with symbol exists."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_result.scalar.return_value = 1  # COUNT(*) returns 1
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)
        symbol = StockSymbol("AAPL")

        # Act
        result = repository.exists_by_symbol(symbol)

        # Assert
        assert result is True

        # Verify the select statement
        call_args = mock_connection.execute.call_args
        statement = call_args[0][0]
        assert statement.is_select

    def test_exists_by_symbol_returns_false_when_stock_not_exists(self) -> None:
        """Should return False when stock with symbol does not exist."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_result.scalar.return_value = 0  # COUNT(*) returns 0
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)
        symbol = StockSymbol("NONE")

        # Act
        result = repository.exists_by_symbol(symbol)

        # Assert
        assert result is False

    def test_exists_by_symbol_handles_database_errors(self) -> None:
        """Should propagate database errors."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_connection.execute.side_effect = exc.DatabaseError(
            "Database connection lost", params={}, orig=None
        )

        repository = SqlAlchemyStockRepository(mock_connection)
        symbol = StockSymbol("AAPL")

        # Act & Assert
        with pytest.raises(exc.DatabaseError):
            repository.exists_by_symbol(symbol)


class TestSqlAlchemyStockRepositorySearchStocks:
    """Test the search_stocks method of the repository."""

    def test_search_stocks_returns_all_when_no_filters(self) -> None:
        """Should return all stocks when no filters are provided."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()

        mock_rows = [
            {
                "id": "stock-1",
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry_group": "Hardware",
                "grade": "A",
                "notes": "",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": "stock-2",
                "symbol": "MSFT",
                "company_name": "Microsoft Corporation",
                "sector": "Technology",
                "industry_group": "Software",
                "grade": "B",
                "notes": "",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ]

        mock_result.fetchall.return_value = mock_rows
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.search_stocks()

        # Assert
        assert len(result) == 2
        assert all(isinstance(stock, Stock) for stock in result)

    def test_search_stocks_filters_by_symbol(self) -> None:
        """Should filter stocks by symbol pattern."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()

        mock_rows = [
            {
                "id": "stock-1",
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry_group": "Hardware",
                "grade": "A",
                "notes": "",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        ]

        mock_result.fetchall.return_value = mock_rows
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.search_stocks(symbol_filter="AA")

        # Assert
        assert len(result) == 1
        assert result[0].symbol.value == "AAPL"

        # Verify the query includes LIKE clause
        call_args = mock_connection.execute.call_args
        statement = call_args[0][0]
        assert statement.whereclause is not None

    def test_search_stocks_filters_by_company_name(self) -> None:
        """Should filter stocks by company name pattern."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()

        mock_rows = [
            {
                "id": "stock-1",
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry_group": "Hardware",
                "grade": "A",
                "notes": "",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        ]

        mock_result.fetchall.return_value = mock_rows
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.search_stocks(name_filter="Apple")

        # Assert
        assert len(result) == 1
        assert result[0].company_name is not None
        assert result[0].company_name.value == "Apple Inc."

    def test_search_stocks_filters_by_sector(self) -> None:
        """Should filter stocks by exact sector match."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()

        mock_rows = [
            {
                "id": "stock-1",
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry_group": "Hardware",
                "grade": "A",
                "notes": "",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": "stock-2",
                "symbol": "MSFT",
                "company_name": "Microsoft Corporation",
                "sector": "Technology",
                "industry_group": "Software",
                "grade": "B",
                "notes": "",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ]

        mock_result.fetchall.return_value = mock_rows
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.search_stocks(sector_filter="Technology")

        # Assert
        assert len(result) == 2
        assert all(
            stock.sector and stock.sector.value == "Technology" for stock in result
        )

    def test_search_stocks_filters_by_industry_group(self) -> None:
        """Should filter stocks by exact industry group match."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()

        mock_rows = [
            {
                "id": "stock-1",
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry_group": "Hardware",
                "grade": "A",
                "notes": "",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        ]

        mock_result.fetchall.return_value = mock_rows
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.search_stocks(industry_filter="Hardware")

        # Assert
        assert len(result) == 1
        assert result[0].industry_group is not None
        assert result[0].industry_group.value == "Hardware"

    def test_search_stocks_filters_by_grade(self) -> None:
        """Should filter stocks by exact grade match."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()

        mock_rows = [
            {
                "id": "stock-1",
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry_group": "Hardware",
                "grade": "A",
                "notes": "",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        ]

        mock_result.fetchall.return_value = mock_rows
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.search_stocks(grade_filter="A")

        # Assert
        assert len(result) == 1
        assert result[0].grade is not None
        assert result[0].grade.value == "A"

    def test_search_stocks_combines_multiple_filters(self) -> None:
        """Should combine multiple filters with AND logic."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()

        mock_rows = [
            {
                "id": "stock-1",
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry_group": "Hardware",
                "grade": "A",
                "notes": "",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        ]

        mock_result.fetchall.return_value = mock_rows
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.search_stocks(
            symbol_filter="AA", sector_filter="Technology", grade_filter="A"
        )

        # Assert
        assert len(result) == 1
        assert result[0].symbol.value == "AAPL"

    def test_search_stocks_returns_empty_list_when_no_matches(self) -> None:
        """Should return empty list when no stocks match filters."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_connection.execute.return_value = mock_result

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act
        result = repository.search_stocks(symbol_filter="ZZZZ")

        # Assert
        assert result == []

    def test_search_stocks_handles_database_errors(self) -> None:
        """Should propagate database errors."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        mock_connection.execute.side_effect = exc.DatabaseError(
            "Database connection lost", params={}, orig=None
        )

        repository = SqlAlchemyStockRepository(mock_connection)

        # Act & Assert
        with pytest.raises(exc.DatabaseError):
            repository.search_stocks()


class TestSqlAlchemyStockRepositoryStubMethods:
    """Test that stub methods for unimplemented interface methods exist."""

    def test_no_more_stub_methods(self) -> None:
        """All methods should now be implemented."""
        # Arrange
        mock_connection = Mock(spec=IDatabaseConnection)
        repository = SqlAlchemyStockRepository(mock_connection)

        # Assert - all methods are callable (not raising NotImplementedError)
        assert hasattr(repository, "create")
        assert hasattr(repository, "get_by_id")
        assert hasattr(repository, "get_by_symbol")
        assert hasattr(repository, "get_all")
        assert hasattr(repository, "update")
        assert hasattr(repository, "delete")
        assert hasattr(repository, "exists_by_symbol")
        assert hasattr(repository, "search_stocks")
