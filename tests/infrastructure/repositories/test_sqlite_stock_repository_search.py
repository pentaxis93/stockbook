"""
Tests for SQLite Stock Repository search functionality.

Following TDD approach - these tests define the expected behavior
of the search functionality in the stock repository.
"""

from unittest.mock import Mock

import pytest

from domain.entities.stock_entity import StockEntity
from domain.value_objects.stock_symbol import StockSymbol
from infrastructure.repositories.sqlite_stock_repository import \
    SqliteStockRepository


class TestSqliteStockRepositorySearch:
    """Test suite for SqliteStockRepository search functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock database connection that simulates the SQLite behavior
        self.mock_db_connection = Mock()
        self.mock_connection = Mock()
        self.mock_cursor = Mock()

        self.mock_db_connection.get_connection.return_value = self.mock_connection
        self.mock_connection.execute.return_value = self.mock_cursor

        # Set up the repository
        self.repository = SqliteStockRepository(self.mock_db_connection)

    def test_search_stocks_with_symbol_filter(self):
        """Should search stocks by symbol filter."""
        # Arrange
        symbol_filter = "APP"
        expected_query = "SELECT id, symbol, name, industry_group, grade, notes FROM stock WHERE UPPER(symbol) LIKE UPPER(?) ORDER BY symbol"
        expected_params = ["%APP%"]

        # Mock database results
        mock_rows = [
            {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "",
            },
        ]
        self.mock_cursor.fetchall.return_value = mock_rows

        # Act
        results = self.repository.search_stocks(symbol_filter=symbol_filter)

        # Assert
        self.mock_connection.execute.assert_called_once_with(
            expected_query, expected_params
        )
        assert len(results) == 1
        assert results[0].symbol.value == "AAPL"
        assert results[0].name == "Apple Inc."

    def test_search_stocks_with_name_filter(self):
        """Should search stocks by name filter."""
        # Arrange
        name_filter = "Apple"
        expected_query = "SELECT id, symbol, name, industry_group, grade, notes FROM stock WHERE UPPER(name) LIKE UPPER(?) ORDER BY symbol"
        expected_params = ["%Apple%"]

        # Mock database results
        mock_rows = [
            {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "",
            },
        ]
        self.mock_cursor.fetchall.return_value = mock_rows

        # Act
        results = self.repository.search_stocks(name_filter=name_filter)

        # Assert
        self.mock_connection.execute.assert_called_once_with(
            expected_query, expected_params
        )
        assert len(results) == 1
        assert results[0].name == "Apple Inc."

    def test_search_stocks_with_industry_filter(self):
        """Should search stocks by industry filter."""
        # Arrange
        industry_filter = "Tech"
        expected_query = "SELECT id, symbol, name, industry_group, grade, notes FROM stock WHERE UPPER(industry_group) LIKE UPPER(?) ORDER BY symbol"
        expected_params = ["%Tech%"]

        # Mock database results
        mock_rows = [
            {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "",
            },
            {
                "id": 2,
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "",
            },
        ]
        self.mock_cursor.fetchall.return_value = mock_rows

        # Act
        results = self.repository.search_stocks(industry_filter=industry_filter)

        # Assert
        self.mock_connection.execute.assert_called_once_with(
            expected_query, expected_params
        )
        assert len(results) == 2

    def test_search_stocks_with_grade_filter(self):
        """Should search stocks by grade filter."""
        # Arrange
        grade_filter = "A"
        expected_query = "SELECT id, symbol, name, industry_group, grade, notes FROM stock WHERE grade = ? ORDER BY symbol"
        expected_params = ["A"]

        # Mock database results
        mock_rows = [
            {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "",
            },
            {
                "id": 2,
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "",
            },
        ]
        self.mock_cursor.fetchall.return_value = mock_rows

        # Act
        results = self.repository.search_stocks(grade_filter=grade_filter)

        # Assert
        self.mock_connection.execute.assert_called_once_with(
            expected_query, expected_params
        )
        assert len(results) == 2
        assert all(stock.grade == "A" for stock in results)

    def test_search_stocks_with_multiple_filters(self):
        """Should search stocks with multiple filter criteria."""
        # Arrange
        symbol_filter = "G"
        grade_filter = "A"
        expected_query = "SELECT id, symbol, name, industry_group, grade, notes FROM stock WHERE UPPER(symbol) LIKE UPPER(?) AND grade = ? ORDER BY symbol"
        expected_params = ["%G%", "A"]

        # Mock database results
        mock_rows = [
            {
                "id": 2,
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "",
            },
        ]
        self.mock_cursor.fetchall.return_value = mock_rows

        # Act
        results = self.repository.search_stocks(
            symbol_filter=symbol_filter, grade_filter=grade_filter
        )

        # Assert
        self.mock_connection.execute.assert_called_once_with(
            expected_query, expected_params
        )
        assert len(results) == 1
        assert results[0].symbol.value == "GOOGL"
        assert results[0].grade == "A"

    def test_search_stocks_with_all_filters(self):
        """Should search stocks with all filter criteria."""
        # Arrange
        symbol_filter = "APP"
        name_filter = "Apple"
        industry_filter = "Tech"
        grade_filter = "A"
        expected_query = (
            "SELECT id, symbol, name, industry_group, grade, notes FROM stock "
            "WHERE UPPER(symbol) LIKE UPPER(?) AND UPPER(name) LIKE UPPER(?) "
            "AND UPPER(industry_group) LIKE UPPER(?) AND grade = ? ORDER BY symbol"
        )
        expected_params = ["%APP%", "%Apple%", "%Tech%", "A"]

        # Mock database results
        mock_rows = [
            {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "",
            },
        ]
        self.mock_cursor.fetchall.return_value = mock_rows

        # Act
        results = self.repository.search_stocks(
            symbol_filter=symbol_filter,
            name_filter=name_filter,
            industry_filter=industry_filter,
            grade_filter=grade_filter,
        )

        # Assert
        self.mock_connection.execute.assert_called_once_with(
            expected_query, expected_params
        )
        assert len(results) == 1
        assert results[0].symbol.value == "AAPL"

    def test_search_stocks_with_no_filters(self):
        """Should return all stocks when no filters are provided."""
        # Arrange
        expected_query = "SELECT id, symbol, name, industry_group, grade, notes FROM stock ORDER BY symbol"
        expected_params = []

        # Mock database results
        mock_rows = [
            {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "",
            },
            {
                "id": 2,
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "",
            },
            {
                "id": 3,
                "symbol": "MSFT",
                "name": "Microsoft Corp.",
                "industry_group": "Technology",
                "grade": "B",
                "notes": "",
            },
        ]
        self.mock_cursor.fetchall.return_value = mock_rows

        # Act
        results = self.repository.search_stocks()

        # Assert
        self.mock_connection.execute.assert_called_once_with(
            expected_query, expected_params
        )
        assert len(results) == 3

    def test_search_stocks_empty_results(self):
        """Should handle empty search results gracefully."""
        # Arrange
        symbol_filter = "NOTFOUND"
        expected_query = "SELECT id, symbol, name, industry_group, grade, notes FROM stock WHERE UPPER(symbol) LIKE UPPER(?) ORDER BY symbol"
        expected_params = ["%NOTFOUND%"]

        # Mock database results
        self.mock_cursor.fetchall.return_value = []

        # Act
        results = self.repository.search_stocks(symbol_filter=symbol_filter)

        # Assert
        self.mock_connection.execute.assert_called_once_with(
            expected_query, expected_params
        )
        assert len(results) == 0

    def test_search_stocks_case_insensitive(self):
        """Should perform case-insensitive searches."""
        # Arrange
        symbol_filter = "app"  # lowercase
        expected_query = "SELECT id, symbol, name, industry_group, grade, notes FROM stock WHERE UPPER(symbol) LIKE UPPER(?) ORDER BY symbol"
        expected_params = ["%app%"]

        # Mock database results
        mock_rows = [
            {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "",
            },
        ]
        self.mock_cursor.fetchall.return_value = mock_rows

        # Act
        results = self.repository.search_stocks(symbol_filter=symbol_filter)

        # Assert
        self.mock_connection.execute.assert_called_once_with(
            expected_query, expected_params
        )
        assert len(results) == 1
        assert results[0].symbol.value == "AAPL"

    def test_search_stocks_connection_cleanup(self):
        """Should properly handle database connection cleanup."""
        # Arrange
        symbol_filter = "AAPL"
        mock_rows = [
            {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "",
            },
        ]
        self.mock_cursor.fetchall.return_value = mock_rows

        # Mock the is_transactional check
        self.mock_db_connection.is_transactional = False

        # Act
        results = self.repository.search_stocks(symbol_filter=symbol_filter)

        # Assert
        assert len(results) == 1
        self.mock_connection.close.assert_called_once()

    def test_search_stocks_entity_mapping(self):
        """Should properly map database rows to domain entities."""
        # Arrange
        symbol_filter = "AAPL"
        mock_rows = [
            {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "High quality stock",
            },
        ]
        self.mock_cursor.fetchall.return_value = mock_rows

        # Act
        results = self.repository.search_stocks(symbol_filter=symbol_filter)

        # Assert
        assert len(results) == 1
        stock = results[0]
        assert isinstance(stock, StockEntity)
        assert isinstance(stock.symbol, StockSymbol)
        assert stock.id == 1
        assert stock.symbol.value == "AAPL"
        assert stock.name == "Apple Inc."
        assert stock.industry_group == "Technology"
        assert stock.grade == "A"
        assert stock.notes == "High quality stock"
