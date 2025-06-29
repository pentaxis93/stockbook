"""
Tests for Stock Controller in presentation layer.

Following TDD approach - these tests define the expected behavior
of the stock controller that coordinates between UI and application services.
"""

from unittest.mock import Mock

from src.application.commands.stock_commands import CreateStockCommand
from src.application.dto.stock_dto import StockDto
from src.application.services.stock_application_service import StockApplicationService
from src.presentation.controllers.stock_controller import StockController
from src.presentation.view_models.stock_view_models import (
    CreateStockRequest,
    CreateStockResponse,
    StockDetailResponse,
    StockListResponse,
    StockSearchRequest,
    UpdateStockRequest,
    UpdateStockResponse,
    ValidationErrorResponse,
)


class TestStockController:
    """Test suite for StockController presentation layer."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_stock_service = Mock(spec=StockApplicationService)
        self.controller = StockController(self.mock_stock_service)

    def test_controller_initialization(self) -> None:
        """Should initialize controller with required dependencies."""
        # Act & Assert
        assert self.controller.stock_service == self.mock_stock_service
        assert hasattr(self.controller, "create_stock")
        assert hasattr(self.controller, "get_stock_list")
        assert hasattr(self.controller, "get_stock_by_symbol")

    def test_create_stock_success(self) -> None:
        """Should successfully create stock through application service."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="High quality stock",
        )

        expected_dto = StockDto(
            id="stock-id-1",
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="High quality stock",
        )

        self.mock_stock_service.create_stock.return_value = expected_dto

        # Act
        response = self.controller.create_stock(request)

        # Assert
        assert isinstance(response, CreateStockResponse)
        assert response.success is True
        assert response.stock_id == "stock-id-1"
        assert response.symbol == "AAPL"
        assert response.message == "Stock created successfully"
        assert response.errors is None

        # Verify service was called with correct command
        self.mock_stock_service.create_stock.assert_called_once()
        call_args = self.mock_stock_service.create_stock.call_args[0][0]
        assert isinstance(call_args, CreateStockCommand)
        assert call_args.symbol == "AAPL"
        assert call_args.name == "Apple Inc."

    def test_create_stock_validation_error(self) -> None:
        """Should handle validation errors gracefully."""
        # Arrange
        request = CreateStockRequest(
            symbol="",  # Invalid empty symbol
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="",
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

    def test_create_stock_service_error(self) -> None:
        """Should handle application service errors."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="",
        )

        self.mock_stock_service.create_stock.side_effect = ValueError(
            "Stock already exists"
        )

        # Act
        response = self.controller.create_stock(request)

        # Assert
        assert isinstance(response, CreateStockResponse)
        assert response.success is False
        assert response.stock_id is None
        assert response.message == "Stock already exists"
        assert response.errors is None

    def test_create_stock_invalid_symbol_format(self) -> None:
        """Should validate stock symbol format."""
        # Arrange
        request = CreateStockRequest(
            symbol="invalid123",  # Invalid format
            name="Test Company",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="",
        )

        # Act
        response = self.controller.create_stock(request)

        # Assert
        assert isinstance(response, ValidationErrorResponse)
        assert response.success is False
        assert "symbol" in response.errors
        assert "Invalid stock symbol format" in response.errors["symbol"]

    def test_create_stock_invalid_grade(self) -> None:
        """Should validate stock grade values."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="Z",  # Invalid grade
            notes="",
        )

        # Act
        response = self.controller.create_stock(request)

        # Assert
        assert isinstance(response, ValidationErrorResponse)
        assert response.success is False
        assert "grade" in response.errors
        assert "Grade must be A, B, C, or empty" in response.errors["grade"]

    def test_get_stock_list_success(self) -> None:
        """Should retrieve stock list successfully."""
        # Arrange
        mock_stocks = [
            StockDto(
                id="stock-id-1",
                symbol="AAPL",
                name="Apple Inc.",
                sector="Technology",
                industry_group="Software",
                grade="A",
                notes="",
            ),
            StockDto(
                id="stock-id-2",
                symbol="GOOGL",
                name="Alphabet Inc.",
                sector="Technology",
                industry_group="Software",
                grade="A",
                notes="",
            ),
            StockDto(
                id="stock-id-3",
                symbol="MSFT",
                name="Microsoft Corp.",
                sector="Technology",
                industry_group="Software",
                grade="B",
                notes="",
            ),
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

    def test_get_stock_list_empty(self) -> None:
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

    def test_get_stock_list_service_error(self) -> None:
        """Should handle service errors in stock list retrieval."""
        # Arrange
        self.mock_stock_service.get_all_stocks.side_effect = Exception("Database error")

        # Act
        response = self.controller.get_stock_list()

        # Assert
        assert isinstance(response, StockListResponse)
        assert response.success is False
        assert not response.stocks
        assert response.message == "Database error"

    def test_get_stock_by_symbol_success(self) -> None:
        """Should retrieve stock by symbol successfully."""
        # Arrange
        symbol = "AAPL"
        mock_stock = StockDto(
            id="stock-id-1",
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="High quality stock",
        )

        self.mock_stock_service.get_stock_by_symbol.return_value = mock_stock

        # Act
        response = self.controller.get_stock_by_symbol(symbol)

        # Assert
        assert isinstance(response, StockDetailResponse)
        assert response.success is True
        assert response.stock is not None
        assert response.stock.symbol == "AAPL"
        assert response.stock.name == "Apple Inc."
        assert response.message == "Stock retrieved successfully"

        # Verify service was called with correct symbol
        self.mock_stock_service.get_stock_by_symbol.assert_called_once_with(symbol)

    def test_get_stock_by_symbol_not_found(self) -> None:
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

    def test_get_stock_by_symbol_invalid_format(self) -> None:
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

    def test_controller_error_handling_generic_exception(self) -> None:
        """Should handle unexpected exceptions gracefully."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="",
        )

        self.mock_stock_service.create_stock.side_effect = Exception("Unexpected error")

        # Act
        response = self.controller.create_stock(request)

        # Assert
        assert isinstance(response, CreateStockResponse)
        assert response.success is False
        assert "Unexpected error" in response.message

    def test_controller_input_sanitization(self) -> None:
        """Should sanitize input data before processing."""
        # Arrange
        request = CreateStockRequest(
            symbol="  aapl  ",  # Needs trimming and uppercase
            name="  Apple Inc.  ",  # Needs trimming
            sector="  Technology  ",
            industry_group="  Software  ",
            grade="a",  # Needs uppercase
            notes="  Some notes  ",
        )

        expected_dto = StockDto(
            id="stock-id-1",
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Some notes",
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
        assert call_args.sector == "Technology"
        assert call_args.industry_group == "Software"
        assert call_args.grade == "A"
        assert call_args.notes == "Some notes"

    def test_controller_concurrent_requests_handling(self) -> None:
        """Should handle concurrent requests safely."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="",
        )

        # Simulate concurrent access scenario
        self.mock_stock_service.create_stock.side_effect = [
            StockDto(
                id="stock-id-1",
                symbol="AAPL",
                name="Apple Inc.",
                sector="Technology",
                industry_group="Software",
                grade="A",
                notes="",
            ),
            ValueError("Stock already exists"),
        ]

        # Act
        response1 = self.controller.create_stock(request)
        response2 = self.controller.create_stock(request)

        # Assert
        assert response1.success is True
        assert response2.success is False
        assert "Stock already exists" in response2.message

    def test_search_stocks_success(self) -> None:
        """Should search stocks successfully with filters."""
        # Arrange
        search_request = StockSearchRequest(
            symbol_filter="APP",
            name_filter="Apple",
            grade_filter="A",
        )

        mock_stocks = [
            StockDto(
                id="stock-id-1",
                symbol="AAPL",
                name="Apple Inc.",
                sector="Technology",
                industry_group="Software",
                grade="A",
                notes="",
            ),
        ]

        self.mock_stock_service.search_stocks.return_value = mock_stocks

        # Act
        response = self.controller.search_stocks(search_request)

        # Assert
        assert isinstance(response, StockListResponse)
        assert response.success is True
        assert len(response.stocks) == 1
        assert response.stocks[0].symbol == "AAPL"
        assert response.filters_applied == {
            "symbol": "APP",
            "name": "Apple",
            "grade": "A",
        }
        assert "Retrieved 1 stock" in response.message

        # Verify service was called with correct parameters
        self.mock_stock_service.search_stocks.assert_called_once_with(
            symbol_filter="APP",
            name_filter="Apple",
            industry_filter=None,
            grade_filter="A",
        )

    def test_search_stocks_no_filters_fallback(self) -> None:
        """Should fallback to get_stock_list when no filters are provided."""
        # Arrange
        search_request = StockSearchRequest()  # No filters

        mock_stocks = [
            StockDto(
                id="stock-id-1",
                symbol="AAPL",
                name="Apple Inc.",
                sector="Technology",
                industry_group="Software",
                grade="A",
                notes="",
            ),
            StockDto(
                id="stock-id-2",
                symbol="GOOGL",
                name="Alphabet Inc.",
                sector="Technology",
                industry_group="Software",
                grade="A",
                notes="",
            ),
        ]

        self.mock_stock_service.get_all_stocks.return_value = mock_stocks

        # Act
        response = self.controller.search_stocks(search_request)

        # Assert
        assert isinstance(response, StockListResponse)
        assert response.success is True
        assert len(response.stocks) == 2
        assert response.message == "Retrieved 2 stocks"

        # Verify get_all_stocks was called instead of search_stocks
        self.mock_stock_service.get_all_stocks.assert_called_once()
        self.mock_stock_service.search_stocks.assert_not_called()

    def test_search_stocks_validation_error(self) -> None:
        """Should handle validation errors in search request."""
        # Arrange
        search_request = StockSearchRequest(
            grade_filter="Z",  # Invalid grade
        )

        # Act
        response = self.controller.search_stocks(search_request)

        # Assert
        assert isinstance(response, ValidationErrorResponse)
        assert response.success is False
        assert "grade_filter" in response.errors
        assert "Grade must be A, B, or C" in response.errors["grade_filter"]

        # Service should not be called
        self.mock_stock_service.search_stocks.assert_not_called()

    def test_search_stocks_empty_results(self) -> None:
        """Should handle empty search results gracefully."""
        # Arrange
        search_request = StockSearchRequest(symbol_filter="NOTFOUND")

        self.mock_stock_service.search_stocks.return_value = []

        # Act
        response = self.controller.search_stocks(search_request)

        # Assert
        assert isinstance(response, StockListResponse)
        assert response.success is True
        assert len(response.stocks) == 0
        assert "Retrieved 0 stocks" in response.message
        assert response.filters_applied == {"symbol": "NOTFOUND"}

    def test_search_stocks_service_error(self) -> None:
        """Should handle application service errors in search."""
        # Arrange
        search_request = StockSearchRequest(symbol_filter="AAPL")

        self.mock_stock_service.search_stocks.side_effect = Exception("Database error")

        # Act
        response = self.controller.search_stocks(search_request)

        # Assert
        assert isinstance(response, StockListResponse)
        assert response.success is False
        assert response.message == "Database error"

    def test_search_stocks_filter_message_formatting(self) -> None:
        """Should format filter messages correctly based on filter count."""
        # Arrange
        # Test single filter
        search_request_single = StockSearchRequest(symbol_filter="AAPL")
        self.mock_stock_service.search_stocks.return_value = [
            StockDto(id="stock-id-1", symbol="AAPL", name="Apple Inc.", grade="A")
        ]

        response_single = self.controller.search_stocks(search_request_single)
        assert "symbol containing 'AAPL'" in response_single.message

        # Test multiple filters
        search_request_multi = StockSearchRequest(symbol_filter="A", grade_filter="A")
        self.mock_stock_service.search_stocks.return_value = [
            StockDto(id="stock-id-1", symbol="AAPL", name="Apple Inc.", grade="A")
        ]

        response_multi = self.controller.search_stocks(search_request_multi)
        assert "matching 2 filters" in response_multi.message

    def test_update_stock_with_valid_request(self) -> None:
        """Should update stock successfully with valid request."""
        # Arrange
        request = UpdateStockRequest(
            stock_id="stock-id-1",
            name="Apple Inc. (Updated)",
            industry_group="Consumer Electronics",
            grade="A",
            notes="Updated notes",
        )

        expected_dto = StockDto(
            id="stock-id-1",
            symbol="AAPL",
            name="Apple Inc. (Updated)",
            industry_group="Consumer Electronics",
            grade="A",
            notes="Updated notes",
        )

        self.mock_stock_service.update_stock.return_value = expected_dto

        # Act
        response = self.controller.update_stock(request)

        # Assert
        assert isinstance(response, UpdateStockResponse)
        assert response.success is True
        assert response.stock_id == "stock-id-1"
        assert "Stock updated successfully" in response.message

    def test_update_stock_with_validation_errors(self) -> None:
        """Should return validation errors for invalid update request."""
        # Arrange
        request = UpdateStockRequest(
            stock_id="stock-id-1",
            name="",  # Invalid empty name
            grade="Z",  # Invalid grade
        )

        # Act
        response = self.controller.update_stock(request)

        # Assert
        assert isinstance(response, ValidationErrorResponse)
        assert "name" in response.errors
        assert "grade" in response.errors

    def test_update_stock_with_nonexistent_stock(self) -> None:
        """Should handle update of nonexistent stock."""
        # Arrange
        request = UpdateStockRequest(stock_id="stock-id-999", grade="A")

        self.mock_stock_service.update_stock.side_effect = ValueError(
            "Stock with ID stock-id-999 not found"
        )

        # Act
        response = self.controller.update_stock(request)

        # Assert
        assert isinstance(response, UpdateStockResponse)
        assert response.success is False
        assert "Stock with ID stock-id-999 not found" in response.message

    def test_update_stock_with_no_fields_to_update(self) -> None:
        """Should handle update request with no fields to update."""
        # Arrange
        request = UpdateStockRequest(stock_id="stock-id-1")  # No fields to update

        # Act
        response = self.controller.update_stock(request)

        # Assert
        assert isinstance(response, ValidationErrorResponse)
        assert "No fields to update" in response.errors.get("general", "")

    def test_update_stock_with_service_error(self) -> None:
        """Should handle application service errors during update."""
        # Arrange
        request = UpdateStockRequest(stock_id="stock-id-1", grade="A")

        self.mock_stock_service.update_stock.side_effect = Exception("Database error")

        # Act
        response = self.controller.update_stock(request)

        # Assert
        assert isinstance(response, UpdateStockResponse)
        assert response.success is False
        assert "Unexpected error: Database error" in response.message

    def test_create_stock_with_missing_id_in_response(self) -> None:
        """Should handle case when created stock DTO has no ID."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL", name="Apple Inc.", sector="Technology", grade="A"
        )

        # Mock service to return DTO without ID
        stock_dto_without_id = StockDto(
            id=None,  # Missing ID
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group=None,
            grade="A",
            notes="",
        )
        self.mock_stock_service.create_stock.return_value = stock_dto_without_id

        # Act
        response = self.controller.create_stock(request)

        # Assert
        assert isinstance(response, CreateStockResponse)
        assert response.success is False
        assert "Created stock should have a valid ID" in response.message

    def test_get_stock_by_symbol_empty_symbol_validation(self) -> None:
        """Should return validation error for empty symbol."""
        # Act
        result = self.controller.get_stock_by_symbol("")

        # Assert
        assert isinstance(result, ValidationErrorResponse)
        assert "symbol" in result.errors
        assert "Symbol cannot be empty" in result.errors["symbol"]

    def test_update_stock_with_missing_id_in_response(self) -> None:
        """Should handle case when updated stock DTO has no ID."""
        # Arrange
        request = UpdateStockRequest(
            stock_id="stock-123", name="Updated Apple Inc.", sector="Technology"
        )

        # Mock service to return DTO without ID
        stock_dto_without_id = StockDto(
            id=None,  # Missing ID
            symbol="AAPL",
            name="Updated Apple Inc.",
            sector="Technology",
            industry_group=None,
            grade="A",
            notes="",
        )
        self.mock_stock_service.update_stock.return_value = stock_dto_without_id

        # Act
        response = self.controller.update_stock(request)

        # Assert
        assert isinstance(response, UpdateStockResponse)
        assert response.success is False
        assert "Updated stock should have a valid ID" in response.message

    def test_search_stocks_no_filters_message_formatting(self) -> None:
        """Should format message correctly when no filters are applied."""
        # Arrange
        request = StockSearchRequest()  # No filters

        # Mock service response
        stock_dtos = [
            StockDto("1", "AAPL", "Apple Inc.", "Technology", None, "A", ""),
            StockDto("2", "GOOGL", "Google Inc.", "Technology", None, "A", ""),
        ]
        self.mock_stock_service.get_all_stocks.return_value = stock_dtos

        # Act
        result = self.controller.search_stocks(request)

        # Assert
        assert isinstance(result, StockListResponse)
        assert result.success
        assert "Retrieved 2 stocks" in result.message
        assert len(result.stocks) == 2

    def test_search_stocks_empty_active_filters_message(self) -> None:
        """Should format message correctly when active_filters is empty but search_stocks is called."""
        # Arrange - Create a mock request that has_filters=True but active_filters={}
        mock_request = Mock()
        mock_request.has_filters = True
        mock_request.active_filters = {}
        mock_request.symbol_filter = "A"
        mock_request.name_filter = None
        mock_request.industry_filter = None
        mock_request.grade_filter = None
        mock_request.validate.return_value = {}

        stock_dtos = [
            StockDto("1", "AAPL", "Apple Inc.", "Technology", None, "A", ""),
        ]
        self.mock_stock_service.search_stocks.return_value = stock_dtos

        # Act
        result = self.controller.search_stocks(mock_request)

        # Assert
        assert isinstance(result, StockListResponse)
        assert result.success
        assert "Retrieved 1 stocks" in result.message  # Line 235 - filter_count == 0
