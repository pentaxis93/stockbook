"""
Tests for Stock Page Coordinator in presentation layer.

Following TDD approach - these tests define the expected behavior
of the page coordinator that provides data-focused operations for stock management.
"""

from unittest.mock import Mock

from src.presentation.adapters.stock_presentation_adapter import (
    StockPresentationAdapter,
)
from src.presentation.controllers.stock_controller import StockController
from src.presentation.coordinators.stock_page_coordinator import StockPageCoordinator
from src.presentation.view_models.stock_view_models import (
    StockDetailResponse,
    StockListResponse,
    StockViewModel,
    ValidationErrorResponse,
)


class TestStockPageCoordinator:
    """Test suite for StockPageCoordinator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=StockController)
        self.mock_presentation_adapter = Mock(spec=StockPresentationAdapter)
        self.coordinator = StockPageCoordinator(
            self.mock_controller, self.mock_presentation_adapter
        )

    def test_coordinator_initialization(self) -> None:
        """Should initialize coordinator with required dependencies."""
        # Act & Assert
        assert self.coordinator.controller == self.mock_controller
        assert self.coordinator.presentation_adapter == self.mock_presentation_adapter
        assert hasattr(self.coordinator, "get_dashboard_data")
        assert hasattr(self.coordinator, "get_stock_management_data")
        assert hasattr(self.coordinator, "get_stock_detail_data")
        assert hasattr(self.coordinator, "calculate_stock_metrics")

    def test_get_dashboard_data_success(self) -> None:
        """Should return dashboard data instead of rendering UI."""
        # Arrange
        stock_view_model = StockViewModel(
            id="stock-id-1", symbol="AAPL", name="Apple Inc.", grade="A"
        )
        stock_list_response = StockListResponse.create_success(
            [stock_view_model], "Retrieved 1 stock"
        )

        self.mock_controller.get_stock_list.return_value = stock_list_response

        # Act
        result = self.coordinator.get_dashboard_data()

        # Assert
        assert result is not None
        assert "stocks" in result
        assert "metrics" in result
        assert "tabs_config" in result
        assert result["stocks"] == [stock_view_model]

        # Verify metrics calculation
        expected_metrics = {
            "total_stocks": 1,
            "grade_a_count": 1,
            "grade_b_count": 0,
            "grade_c_count": 0,
            "high_grade_percentage": 100.0,
        }
        assert result["metrics"] == expected_metrics

        # Verify tabs configuration
        expected_tabs = ["All Stocks", "By Grade", "Add Stock"]
        assert result["tabs_config"] == expected_tabs

    def test_get_dashboard_data_empty_stocks(self) -> None:
        """Should handle empty stock list in dashboard data."""
        # Arrange
        empty_response = StockListResponse.create_success([], "No stocks found")
        self.mock_controller.get_stock_list.return_value = empty_response

        # Act
        result = self.coordinator.get_dashboard_data()

        # Assert
        assert result is not None
        assert result["stocks"] == []
        assert result["metrics"]["total_stocks"] == 0
        assert result["metrics"]["high_grade_percentage"] == 0.0

    def test_get_stock_management_data_success(self) -> None:
        """Should return stock management data instead of rendering UI."""
        # Arrange
        stock_view_model = StockViewModel(
            id="stock-id-1", symbol="AAPL", name="Apple Inc.", grade="A"
        )
        stock_list_response = StockListResponse.create_success(
            [stock_view_model], "Retrieved 1 stock"
        )

        self.mock_controller.get_stock_list.return_value = stock_list_response

        # Act
        result = self.coordinator.get_stock_management_data("list")

        # Assert
        assert result is not None
        assert "action" in result
        assert "data" in result
        assert "navigation_options" in result
        assert result["action"] == "list"
        assert result["data"] == [stock_view_model]

        expected_nav_options = ["list", "create", "search"]
        assert result["navigation_options"] == expected_nav_options

    def test_get_stock_detail_data_success(self) -> None:
        """Should return stock detail data instead of rendering UI."""
        # Arrange
        stock = StockViewModel(
            id="stock-id-1",
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="High quality stock",
        )

        detail_response = StockDetailResponse.create_success(stock, "Stock retrieved")
        self.mock_controller.get_stock_by_symbol.return_value = detail_response

        # Act
        result = self.coordinator.get_stock_detail_data("AAPL")

        # Assert
        assert result is not None
        assert "stock" in result
        assert "sections" in result
        assert result["stock"] == stock

        # Verify detail sections are configured
        expected_sections = ["basic_info", "additional_info", "notes"]
        assert all(section in result["sections"] for section in expected_sections)

        # Verify controller was called correctly
        self.mock_controller.get_stock_by_symbol.assert_called_once_with("AAPL")

    def test_calculate_stock_metrics(self) -> None:
        """Should calculate stock metrics correctly."""
        # Arrange
        stocks = [
            StockViewModel(
                id="stock-id-1", symbol="AAPL", name="Apple Inc.", grade="A"
            ),
            StockViewModel(
                id="stock-id-2", symbol="GOOGL", name="Alphabet Inc.", grade="A"
            ),
            StockViewModel(
                id="stock-id-3", symbol="MSFT", name="Microsoft Corp.", grade="B"
            ),
            StockViewModel(id="stock-id-4", symbol="IBM", name="IBM Corp.", grade="C"),
        ]

        # Act
        metrics = self.coordinator.calculate_stock_metrics(stocks)

        # Assert
        assert metrics["total_stocks"] == 4
        assert metrics["grade_a_count"] == 2
        assert metrics["grade_b_count"] == 1
        assert metrics["grade_c_count"] == 1
        assert metrics["high_grade_percentage"] == 50.0  # (2/4) * 100

    def test_calculate_stock_metrics_empty_list(self) -> None:
        """Should handle empty stock list in metrics calculation."""
        # Act
        metrics = self.coordinator.calculate_stock_metrics([])

        # Assert
        assert metrics["total_stocks"] == 0
        assert metrics["grade_a_count"] == 0
        assert metrics["grade_b_count"] == 0
        assert metrics["grade_c_count"] == 0
        assert metrics["high_grade_percentage"] == 0.0

    def test_get_stock_management_data_create_action(self) -> None:
        """Should return form data for create action."""
        # Act
        result = self.coordinator.get_stock_management_data("create")

        # Assert
        assert result is not None
        assert result["action"] == "create"
        assert "form_fields" in result["data"]
        assert "validation_rules" in result["data"]

        expected_fields = [
            "symbol",
            "name",
            "sector",
            "industry_group",
            "grade",
            "notes",
        ]
        assert result["data"]["form_fields"] == expected_fields

        expected_rules = {
            "symbol": "required|max:5|alpha",
            "name": "required|max:200",
            "grade": "in:A,B,C",
        }
        assert result["data"]["validation_rules"] == expected_rules

    def test_get_stock_management_data_search_action(self) -> None:
        """Should return search form data for search action."""
        # Act
        result = self.coordinator.get_stock_management_data("search")

        # Assert
        assert result is not None
        assert result["action"] == "search"
        assert "search_fields" in result["data"]
        assert "filter_options" in result["data"]

        expected_fields = ["symbol", "name", "sector", "grade"]
        assert result["data"]["search_fields"] == expected_fields

        expected_options = {
            "grade": ["A", "B", "C"],
            "sector": [],  # Would be populated from existing stocks
        }
        assert result["data"]["filter_options"] == expected_options

    def test_get_stock_management_data_default_action(self) -> None:
        """Should default to list action for unknown actions."""
        # Arrange
        stock_view_model = StockViewModel(
            id="stock-id-1", symbol="AAPL", name="Apple Inc.", grade="A"
        )
        stock_list_response = StockListResponse.create_success(
            [stock_view_model], "Retrieved 1 stock"
        )
        self.mock_controller.get_stock_list.return_value = stock_list_response

        # Act
        result = self.coordinator.get_stock_management_data("unknown_action")

        # Assert
        assert result is not None
        assert result["action"] == "unknown_action"
        assert result["data"] == [stock_view_model]
        assert result["success"] is True

    def test_get_stock_detail_data_failure(self) -> None:
        """Should handle failure in stock detail retrieval."""
        # Arrange
        detail_response = StockDetailResponse.create_error("Stock not found")
        self.mock_controller.get_stock_by_symbol.return_value = detail_response

        # Act
        result = self.coordinator.get_stock_detail_data("NOTFOUND")

        # Assert
        assert result is not None
        assert result["stock"] is None
        assert result["sections"] == []
        assert result["success"] is False
        assert result["message"] == "Stock not found"

    def test_get_stock_detail_data_validation_error(self) -> None:
        """Should handle validation error response from controller."""
        # Arrange
        validation_response = ValidationErrorResponse(
            {"symbol": "Invalid stock symbol format"}
        )
        self.mock_controller.get_stock_by_symbol.return_value = validation_response

        # Act
        result = self.coordinator.get_stock_detail_data("INVALID$SYMBOL")

        # Assert
        assert result is not None
        assert result["stock"] is None
        assert result["sections"] == []
        assert result["success"] is False
        assert result["message"] == "Validation failed"

    def test_get_stock_detail_data_success_with_none_stock(self) -> None:
        """Should handle case where successful response has None stock (edge case)."""
        # Arrange
        # Create a successful response but with None stock (shouldn't happen in practice)
        detail_response = StockDetailResponse(
            success=True, message="Success", stock=None
        )
        self.mock_controller.get_stock_by_symbol.return_value = detail_response

        # Act
        result = self.coordinator.get_stock_detail_data("AAPL")

        # Assert
        assert result is not None
        assert result["stock"] is None
        assert result["sections"] == []
        assert result["success"] is False
        assert result["message"] == "Stock data is missing"
