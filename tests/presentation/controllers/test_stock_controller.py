"""
Tests for Stock Controller in presentation layer.

Following TDD approach - these tests define the expected behavior
of the stock controller that coordinates between UI and application services.
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime

from presentation.controllers.stock_controller import StockController
from presentation.view_models.stock_view_models import (
    CreateStockRequest, StockListResponse, StockDetailResponse, 
    CreateStockResponse, ValidationErrorResponse
)
from application.services.stock_application_service import StockApplicationService
from application.commands.stock_commands import CreateStockCommand
from application.dto.stock_dto import StockDto
from domain.value_objects.stock_symbol import StockSymbol
from domain.entities.stock_entity import StockEntity


class TestStockController:
    """Test suite for StockController presentation layer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_stock_service = Mock(spec=StockApplicationService)
        self.controller = StockController(self.mock_stock_service)
    
    def test_controller_initialization(self):
        """Should initialize controller with required dependencies."""
        # Act & Assert
        assert self.controller.stock_service == self.mock_stock_service
        assert hasattr(self.controller, 'create_stock')
        assert hasattr(self.controller, 'get_stock_list')
        assert hasattr(self.controller, 'get_stock_by_symbol')
    
    def test_create_stock_success(self):
        """Should successfully create stock through application service."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes="High quality stock"
        )
        
        expected_dto = StockDto(
            id=1,
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology", 
            grade="A",
            notes="High quality stock"
        )
        
        self.mock_stock_service.create_stock.return_value = expected_dto
        
        # Act
        response = self.controller.create_stock(request)
        
        # Assert
        assert isinstance(response, CreateStockResponse)
        assert response.success is True
        assert response.stock_id == 1
        assert response.symbol == "AAPL"
        assert response.message == "Stock created successfully"
        assert response.errors is None
        
        # Verify service was called with correct command
        self.mock_stock_service.create_stock.assert_called_once()
        call_args = self.mock_stock_service.create_stock.call_args[0][0]
        assert isinstance(call_args, CreateStockCommand)
        assert call_args.symbol == "AAPL"
        assert call_args.name == "Apple Inc."
    
    def test_create_stock_validation_error(self):
        """Should handle validation errors gracefully."""
        # Arrange
        request = CreateStockRequest(
            symbol="",  # Invalid empty symbol
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes=""
        )
        
        # Act
        response = self.controller.create_stock(request)
        
        # Assert
        assert isinstance(response, ValidationErrorResponse)
        assert response.success is False
        assert "symbol" in response.errors
        assert response.errors["symbol"] == "Stock symbol cannot be empty"
        assert response.message == "Validation failed"
        
        # Service should not be called
        self.mock_stock_service.create_stock.assert_not_called()
    
    def test_create_stock_service_error(self):
        """Should handle application service errors."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes=""
        )
        
        self.mock_stock_service.create_stock.side_effect = ValueError("Stock already exists")
        
        # Act
        response = self.controller.create_stock(request)
        
        # Assert
        assert isinstance(response, CreateStockResponse)
        assert response.success is False
        assert response.stock_id is None
        assert response.message == "Stock already exists"
        assert response.errors is None
    
    def test_create_stock_invalid_symbol_format(self):
        """Should validate stock symbol format."""
        # Arrange
        request = CreateStockRequest(
            symbol="invalid123",  # Invalid format
            name="Test Company",
            industry_group="Technology",
            grade="A",
            notes=""
        )
        
        # Act
        response = self.controller.create_stock(request)
        
        # Assert
        assert isinstance(response, ValidationErrorResponse)
        assert response.success is False
        assert "symbol" in response.errors
        assert "Invalid stock symbol format" in response.errors["symbol"]
    
    def test_create_stock_invalid_grade(self):
        """Should validate stock grade values."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="Z",  # Invalid grade
            notes=""
        )
        
        # Act
        response = self.controller.create_stock(request)
        
        # Assert
        assert isinstance(response, ValidationErrorResponse)
        assert response.success is False
        assert "grade" in response.errors
        assert "Grade must be A, B, C, or empty" in response.errors["grade"]
    
    def test_get_stock_list_success(self):
        """Should retrieve stock list successfully."""
        # Arrange
        mock_stocks = [
            StockDto(id=1, symbol="AAPL", name="Apple Inc.", industry_group="Technology", grade="A", notes=""),
            StockDto(id=2, symbol="GOOGL", name="Alphabet Inc.", industry_group="Technology", grade="A", notes=""),
            StockDto(id=3, symbol="MSFT", name="Microsoft Corp.", industry_group="Technology", grade="B", notes="")
        ]
        
        self.mock_stock_service.get_all_stocks.return_value = mock_stocks
        
        # Act
        response = self.controller.get_stock_list()
        
        # Assert
        assert isinstance(response, StockListResponse)
        assert response.success is True
        assert len(response.stocks) == 3
        assert response.stocks[0].symbol == "AAPL"
        assert response.stocks[1].symbol == "GOOGL"
        assert response.total_count == 3
        assert response.message == "Retrieved 3 stocks"
    
    def test_get_stock_list_empty(self):
        """Should handle empty stock list."""
        # Arrange
        self.mock_stock_service.get_all_stocks.return_value = []
        
        # Act
        response = self.controller.get_stock_list()
        
        # Assert
        assert isinstance(response, StockListResponse)
        assert response.success is True
        assert len(response.stocks) == 0
        assert response.total_count == 0
        assert response.message == "No stocks found"
    
    def test_get_stock_list_service_error(self):
        """Should handle service errors in stock list retrieval."""
        # Arrange
        self.mock_stock_service.get_all_stocks.side_effect = Exception("Database error")
        
        # Act
        response = self.controller.get_stock_list()
        
        # Assert
        assert isinstance(response, StockListResponse)
        assert response.success is False
        assert response.stocks == []
        assert response.message == "Database error"
    
    def test_get_stock_by_symbol_success(self):
        """Should retrieve stock by symbol successfully."""
        # Arrange
        symbol = "AAPL"
        mock_stock = StockDto(
            id=1, 
            symbol="AAPL", 
            name="Apple Inc.", 
            industry_group="Technology", 
            grade="A", 
            notes="High quality stock"
        )
        
        self.mock_stock_service.get_stock_by_symbol.return_value = mock_stock
        
        # Act
        response = self.controller.get_stock_by_symbol(symbol)
        
        # Assert
        assert isinstance(response, StockDetailResponse)
        assert response.success is True
        assert response.stock.symbol == "AAPL"
        assert response.stock.name == "Apple Inc."
        assert response.message == "Stock retrieved successfully"
        
        # Verify service was called with correct symbol
        self.mock_stock_service.get_stock_by_symbol.assert_called_once_with(symbol)
    
    def test_get_stock_by_symbol_not_found(self):
        """Should handle stock not found scenario."""
        # Arrange
        symbol = "NOTFD"  # Valid format but doesn't exist
        self.mock_stock_service.get_stock_by_symbol.return_value = None
        
        # Act
        response = self.controller.get_stock_by_symbol(symbol)
        
        # Assert
        assert isinstance(response, StockDetailResponse)
        assert response.success is False
        assert response.stock is None
        assert response.message == f"Stock with symbol {symbol} not found"
    
    def test_get_stock_by_symbol_invalid_format(self):
        """Should validate symbol format before service call."""
        # Arrange
        invalid_symbol = "invalid123"
        
        # Act
        response = self.controller.get_stock_by_symbol(invalid_symbol)
        
        # Assert
        assert isinstance(response, ValidationErrorResponse)
        assert response.success is False
        assert "symbol" in response.errors
        assert "Invalid stock symbol format" in response.errors["symbol"]
        
        # Service should not be called
        self.mock_stock_service.get_stock_by_symbol.assert_not_called()
    
    def test_get_stocks_by_grade_success(self):
        """Should retrieve stocks filtered by grade."""
        # Arrange
        grade = "A"
        mock_stocks = [
            StockDto(id=1, symbol="AAPL", name="Apple Inc.", industry_group="Technology", grade="A", notes=""),
            StockDto(id=2, symbol="GOOGL", name="Alphabet Inc.", industry_group="Technology", grade="A", notes="")
        ]
        
        self.mock_stock_service.get_stocks_by_grade.return_value = mock_stocks
        
        # Act
        response = self.controller.get_stocks_by_grade(grade)
        
        # Assert
        assert isinstance(response, StockListResponse)
        assert response.success is True
        assert len(response.stocks) == 2
        assert all(stock.grade == "A" for stock in response.stocks)
        assert response.message == "Retrieved 2 stocks with grade A"
    
    def test_get_stocks_by_grade_invalid_grade(self):
        """Should validate grade parameter."""
        # Arrange
        invalid_grade = "Z"
        
        # Act
        response = self.controller.get_stocks_by_grade(invalid_grade)
        
        # Assert
        assert isinstance(response, ValidationErrorResponse)
        assert response.success is False
        assert "grade" in response.errors
        assert "Grade must be A, B, or C" in response.errors["grade"]
    
    def test_controller_error_handling_generic_exception(self):
        """Should handle unexpected exceptions gracefully."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes=""
        )
        
        self.mock_stock_service.create_stock.side_effect = Exception("Unexpected error")
        
        # Act
        response = self.controller.create_stock(request)
        
        # Assert
        assert isinstance(response, CreateStockResponse)
        assert response.success is False
        assert "Unexpected error" in response.message
    
    def test_controller_input_sanitization(self):
        """Should sanitize input data before processing."""
        # Arrange
        request = CreateStockRequest(
            symbol="  aapl  ",  # Needs trimming and uppercase
            name="  Apple Inc.  ",  # Needs trimming
            industry_group="  Technology  ",
            grade="a",  # Needs uppercase
            notes="  Some notes  "
        )
        
        expected_dto = StockDto(
            id=1,
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes="Some notes"
        )
        
        self.mock_stock_service.create_stock.return_value = expected_dto
        
        # Act
        response = self.controller.create_stock(request)
        
        # Assert
        assert response.success is True
        
        # Verify service was called with sanitized data
        call_args = self.mock_stock_service.create_stock.call_args[0][0]
        assert call_args.symbol == "AAPL"
        assert call_args.name == "Apple Inc."
        assert call_args.industry_group == "Technology"
        assert call_args.grade == "A"
        assert call_args.notes == "Some notes"
    
    def test_controller_concurrent_requests_handling(self):
        """Should handle concurrent requests safely."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes=""
        )
        
        # Simulate concurrent access scenario
        self.mock_stock_service.create_stock.side_effect = [
            StockDto(id=1, symbol="AAPL", name="Apple Inc.", industry_group="Technology", grade="A", notes=""),
            ValueError("Stock already exists")
        ]
        
        # Act
        response1 = self.controller.create_stock(request)
        response2 = self.controller.create_stock(request)
        
        # Assert
        assert response1.success is True
        assert response2.success is False
        assert "Stock already exists" in response2.message