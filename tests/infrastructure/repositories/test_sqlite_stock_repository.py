"""
Tests for SQLite stock repository implementation.

Following TDD approach - these tests define the expected behavior
of the concrete repository implementation.
"""

import os
import tempfile

import pytest

from src.domain.entities.stock_entity import StockEntity
from src.domain.value_objects import CompanyName, Grade, IndustryGroup, Notes
from src.domain.value_objects.sector import Sector
from src.domain.value_objects.stock_symbol import StockSymbol
from src.infrastructure.persistence.database_connection import DatabaseConnection
from src.infrastructure.repositories.sqlite_stock_repository import (
    SqliteStockRepository,
)

# Path import removed - unused


class TestSqliteStockRepository:
    """Test suite for SqliteStockRepository."""

    def setup_method(self) -> None:
        """Set up test database and repository."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

        # Initialize database connection and repository
        self.db_connection = DatabaseConnection(self.temp_db.name)
        self.db_connection.initialize_schema()

        self.repository = SqliteStockRepository(self.db_connection)

    def teardown_method(self) -> None:
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_create_stock_success(self) -> None:
        """Should create stock successfully and return ID."""
        # Arrange
        stock = StockEntity(
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
            sector=Sector("Technology"),
            industry_group=IndustryGroup("Software"),
            grade=Grade("A"),
            notes=Notes("Great company"),
        )

        # Act
        stock_id = self.repository.create(stock)

        # Assert
        assert isinstance(stock_id, str)
        assert stock_id

        # Verify stock was actually created
        retrieved_stock = self.repository.get_by_id(stock_id)
        assert retrieved_stock is not None
        assert str(retrieved_stock.symbol) == "AAPL"
        assert retrieved_stock.company_name.value == "Apple Inc."
        assert retrieved_stock.sector is not None
        assert retrieved_stock.sector.value == "Technology"
        assert retrieved_stock.industry_group is not None
        assert retrieved_stock.industry_group.value == "Software"
        assert retrieved_stock.grade is not None
        assert retrieved_stock.grade.value == "A"
        assert retrieved_stock.notes.value == "Great company"
        assert retrieved_stock.id == stock_id

    def test_create_stock_with_minimal_data(self) -> None:
        """Should create stock with only required fields."""
        # Arrange
        stock = StockEntity(
            symbol=StockSymbol("MSFT"), company_name=CompanyName("Microsoft Corp.")
        )

        # Act
        stock_id = self.repository.create(stock)

        # Assert
        retrieved_stock = self.repository.get_by_id(stock_id)
        assert retrieved_stock is not None
        assert str(retrieved_stock.symbol) == "MSFT"
        assert retrieved_stock.company_name.value == "Microsoft Corp."
        assert retrieved_stock.industry_group is None
        assert retrieved_stock.grade is None
        assert retrieved_stock.notes.value == ""

    def test_create_duplicate_symbol_raises_error(self) -> None:
        """Should raise error when creating stock with duplicate symbol."""
        # Arrange
        stock1 = StockEntity(
            symbol=StockSymbol("AAPL"), company_name=CompanyName("Apple Inc.")
        )
        stock2 = StockEntity(
            symbol=StockSymbol("AAPL"), company_name=CompanyName("Another Apple")
        )

        # Act & Assert
        self.repository.create(stock1)

        with pytest.raises(ValueError, match="Stock with symbol AAPL already exists"):
            self.repository.create(stock2)

    def test_get_by_id_success(self) -> None:
        """Should retrieve stock by ID successfully."""
        # Arrange
        stock = StockEntity(
            symbol=StockSymbol("GOOGL"), company_name=CompanyName("Alphabet Inc.")
        )
        stock_id = self.repository.create(stock)

        # Act
        retrieved_stock = self.repository.get_by_id(stock_id)

        # Assert
        assert retrieved_stock is not None
        assert retrieved_stock.id == stock_id
        assert str(retrieved_stock.symbol) == "GOOGL"
        assert retrieved_stock.company_name.value == "Alphabet Inc."

    def test_get_by_id_not_found(self) -> None:
        """Should return None when stock ID not found."""
        # Act
        result = self.repository.get_by_id("nonexistent-id")

        # Assert
        assert result is None

    def test_get_by_symbol_success(self) -> None:
        """Should retrieve stock by symbol successfully."""
        # Arrange
        stock = StockEntity(
            symbol=StockSymbol("TSLA"), company_name=CompanyName("Tesla Inc.")
        )
        stock_id = self.repository.create(stock)

        # Act
        retrieved_stock = self.repository.get_by_symbol(StockSymbol("TSLA"))

        # Assert
        assert retrieved_stock is not None
        assert retrieved_stock.id == stock_id
        assert str(retrieved_stock.symbol) == "TSLA"
        assert retrieved_stock.company_name.value == "Tesla Inc."

    def test_get_by_symbol_not_found(self) -> None:
        """Should return None when symbol not found."""
        # Act
        result = self.repository.get_by_symbol(StockSymbol("NFND"))

        # Assert
        assert result is None

    def test_get_by_symbol_case_insensitive(self) -> None:
        """Should retrieve stock by symbol case-insensitively."""
        # Arrange
        stock = StockEntity(
            symbol=StockSymbol("AAPL"), company_name=CompanyName("Apple Inc.")
        )
        self.repository.create(stock)

        # Act - symbol is stored as uppercase, so this tests normalization
        result = self.repository.get_by_symbol(StockSymbol("aapl"))

        # Assert
        assert result is not None
        assert str(result.symbol) == "AAPL"

    def test_get_all_empty(self) -> None:
        """Should return empty list when no stocks exist."""
        # Act
        result = self.repository.get_all()

        # Assert
        assert result == []

    def test_get_all_multiple_stocks(self) -> None:
        """Should retrieve all stocks in alphabetical order."""
        # Arrange
        stocks = [
            StockEntity(
                symbol=StockSymbol("MSFT"), company_name=CompanyName("Microsoft")
            ),
            StockEntity(symbol=StockSymbol("AAPL"), company_name=CompanyName("Apple")),
            StockEntity(
                symbol=StockSymbol("GOOGL"), company_name=CompanyName("Alphabet")
            ),
        ]

        for stock in stocks:
            self.repository.create(stock)

        # Act
        result = self.repository.get_all()

        # Assert
        assert len(result) == 3

        # Should be sorted by symbol
        symbols = [str(stock.symbol) for stock in result]
        assert symbols == ["AAPL", "GOOGL", "MSFT"]

        # Verify all data is correct
        for stock in result:
            assert stock.id is not None
            assert stock.symbol is not None
            assert stock.company_name.value is not None

    def test_update_stock_success(self) -> None:
        """Should update stock successfully."""
        # Arrange
        stock = StockEntity(
            symbol=StockSymbol("AMZN"),
            company_name=CompanyName("Amazon.com Inc."),
            grade=Grade("B"),
        )
        stock_id = self.repository.create(stock)

        # Create updated entity (since IDs are immutable)
        updated_stock = StockEntity(
            symbol=stock.symbol,
            company_name=stock.company_name,
            grade=Grade("A"),
            notes=Notes("Excellent company"),
            id=stock_id,
        )

        # Act
        success = self.repository.update(stock_id, updated_stock)

        # Assert
        assert success is True

        # Verify changes were persisted
        updated_stock = self.repository.get_by_id(stock_id)
        assert updated_stock is not None
        assert updated_stock.grade is not None
        assert updated_stock.grade.value == "A"
        assert updated_stock.notes.value == "Excellent company"
        assert updated_stock.company_name.value == "Amazon.com Inc."  # Unchanged

    def test_update_nonexistent_stock_returns_false(self) -> None:
        """Should return False when trying to update non-existent stock."""
        # Arrange
        stock = StockEntity(
            symbol=StockSymbol("FAKE"), company_name=CompanyName("Fake Inc.")
        )

        # Act
        success = self.repository.update("nonexistent-id", stock)

        # Assert
        assert success is False

    def test_delete_stock_success(self) -> None:
        """Should delete stock successfully."""
        # Arrange
        stock = StockEntity(
            symbol=StockSymbol("META"), company_name=CompanyName("Meta Platforms")
        )
        stock_id = self.repository.create(stock)

        # Verify stock exists
        assert self.repository.get_by_id(stock_id) is not None

        # Act
        success = self.repository.delete(stock_id)

        # Assert
        assert success is True

        # Verify stock was deleted
        assert self.repository.get_by_id(stock_id) is None

    def test_delete_nonexistent_stock_returns_false(self) -> None:
        """Should return False when trying to delete non-existent stock."""
        # Act
        success = self.repository.delete("nonexistent-id")

        # Assert
        assert success is False

    def test_exists_by_symbol_true(self) -> None:
        """Should return True when stock exists."""
        # Arrange
        stock = StockEntity(
            symbol=StockSymbol("NVDA"), company_name=CompanyName("NVIDIA Corp.")
        )
        self.repository.create(stock)

        # Act
        result = self.repository.exists_by_symbol(StockSymbol("NVDA"))

        # Assert
        assert result is True

    def test_exists_by_symbol_false(self) -> None:
        """Should return False when stock doesn't exist."""
        # Act
        result = self.repository.exists_by_symbol(StockSymbol("NFND"))

        # Assert
        assert result is False

    def test_exists_by_symbol_case_insensitive(self) -> None:
        """Should check existence case-insensitively."""
        # Arrange
        stock = StockEntity(
            symbol=StockSymbol("IBM"), company_name=CompanyName("IBM Corp.")
        )
        self.repository.create(stock)

        # Act
        result = self.repository.exists_by_symbol(StockSymbol("ibm"))

        # Assert
        assert result is True

    def test_repository_handles_database_errors(self) -> None:
        """Should handle database connection errors gracefully."""
        # Arrange - create repository with invalid database path
        invalid_db = DatabaseConnection("/invalid/path/database.db")
        invalid_repository = SqliteStockRepository(invalid_db)
        stock = StockEntity(
            symbol=StockSymbol("ERR"), company_name=CompanyName("Error Inc.")
        )

        # Act & Assert
        with pytest.raises(Exception):  # Should raise some database-related error
            invalid_repository.create(stock)

    def test_repository_preserves_identity(self) -> None:
        """Should preserve entity identity and value object types."""
        # Arrange
        original_symbol = StockSymbol("JNJ")
        stock = StockEntity(
            symbol=original_symbol,
            company_name=CompanyName("Johnson & Johnson"),
            sector=Sector("Healthcare"),
            industry_group=IndustryGroup("Pharmaceuticals"),
            grade=Grade("A"),
        )

        # Act
        stock_id = self.repository.create(stock)
        retrieved_stock = self.repository.get_by_id(stock_id)

        # Assert
        assert retrieved_stock is not None
        assert isinstance(retrieved_stock.symbol, StockSymbol)
        assert str(retrieved_stock.symbol) == str(original_symbol)
        assert retrieved_stock == stock  # Business equality based on symbol

    def test_concurrent_access_safety(self) -> None:
        """Should handle concurrent access safely."""
        # This is a basic test - in real implementation you'd test with threading
        # Arrange
        stock1 = StockEntity(
            symbol=StockSymbol("AMD"), company_name=CompanyName("AMD Inc.")
        )
        stock2 = StockEntity(
            symbol=StockSymbol("INTC"), company_name=CompanyName("Intel Corp.")
        )

        # Act - simulate concurrent operations
        id1 = self.repository.create(stock1)
        id2 = self.repository.create(stock2)

        # Assert
        assert id1 != id2
        assert self.repository.get_by_id(id1) is not None
        assert self.repository.get_by_id(id2) is not None
