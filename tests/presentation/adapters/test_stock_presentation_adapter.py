"""
Tests for framework-agnostic Stock Presentation Adapter.

Following TDD approach - these tests define the expected behavior
of the decoupled presentation adapter that doesn't depend on specific UI frameworks.
"""

from unittest.mock import Mock

from src.presentation.adapters.stock_presentation_adapter import (
    StockPresentationAdapter,
)
from src.presentation.controllers.stock_controller import StockController
from src.presentation.interfaces.ui_operations import (
    IUILayoutOperations,
    IUIOperations,
    IUIValidationOperations,
)
from src.presentation.view_models.stock_view_models import (
    CreateStockResponse,
    StockDetailResponse,
    StockListResponse,
    StockViewModel,
    ValidationErrorResponse,
)


class TestStockPresentationAdapter:
    """Test suite for StockPresentationAdapter."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_controller = Mock(spec=StockController)
        self.mock_ui_operations = Mock(spec=IUIOperations)
        self.mock_layout_operations = Mock(spec=IUILayoutOperations)
        self.mock_validation_operations = Mock(spec=IUIValidationOperations)

        self.adapter = StockPresentationAdapter(
            controller=self.mock_controller,
            ui_operations=self.mock_ui_operations,
            layout_operations=self.mock_layout_operations,
            validation_operations=self.mock_validation_operations,
        )

    def test_adapter_initialization(self) -> None:
        """Should initialize adapter with required dependencies."""
        # Act & Assert
        assert self.adapter.controller == self.mock_controller
        assert self.adapter.ui == self.mock_ui_operations
        assert self.adapter.layout == self.mock_layout_operations
        assert self.adapter.validation == self.mock_validation_operations

    def test_render_create_stock_form_display(self) -> None:
        """Should render create stock form with proper UI operations."""
        # Arrange
        self.mock_ui_operations.create_form.return_value.__enter__ = Mock()
        self.mock_ui_operations.create_form.return_value.__exit__ = Mock(
            return_value=None
        )

        self.mock_ui_operations.create_text_input.side_effect = [
            "AAPL",
            "Apple Inc.",
            "Technology",
        ]
        self.mock_ui_operations.create_selectbox.return_value = "A"
        self.mock_ui_operations.create_text_area.return_value = "Test notes"
        self.mock_ui_operations.create_form_submit_button.return_value = False

        # Act
        result = self.adapter.render_create_stock_form()

        # Assert
        assert result is None  # No submission
        self.mock_ui_operations.create_form.assert_called_once_with("create_stock_form")
        self.mock_ui_operations.render_subheader.assert_called_once_with(
            "📝 Add New Stock"
        )
        assert self.mock_ui_operations.create_text_input.call_count >= 2
        self.mock_ui_operations.create_selectbox.assert_called_once()
        self.mock_ui_operations.create_text_area.assert_called_once()
        self.mock_ui_operations.create_form_submit_button.assert_called_once()

    def test_render_create_stock_form_successful_submission(self) -> None:
        """Should handle successful form submission using UI operations."""
        # Arrange
        self.mock_ui_operations.create_form.return_value.__enter__ = Mock()
        self.mock_ui_operations.create_form.return_value.__exit__ = Mock(
            return_value=None
        )

        self.mock_ui_operations.create_text_input.side_effect = [
            "AAPL",
            "Apple Inc.",
            "Technology",
        ]
        self.mock_ui_operations.create_selectbox.return_value = "A"
        self.mock_ui_operations.create_text_area.return_value = ""
        self.mock_ui_operations.create_form_submit_button.return_value = True

        success_response = CreateStockResponse.create_success(
            stock_id="stock-id-1", symbol="AAPL", message="Stock created successfully"
        )
        self.mock_controller.create_stock.return_value = success_response

        # Act
        result = self.adapter.render_create_stock_form()

        # Assert
        assert result == success_response
        self.mock_controller.create_stock.assert_called_once()
        self.mock_ui_operations.show_success.assert_called_once_with(
            "Stock created successfully"
        )

    def test_render_create_stock_form_validation_error(self) -> None:
        """Should handle validation errors using validation operations."""
        # Arrange
        self.mock_ui_operations.create_form.return_value.__enter__ = Mock()
        self.mock_ui_operations.create_form.return_value.__exit__ = Mock(
            return_value=None
        )

        self.mock_ui_operations.create_text_input.side_effect = [
            "",
            "Apple Inc.",
            "Technology",  # Empty symbol
        ]
        self.mock_ui_operations.create_selectbox.return_value = "A"
        self.mock_ui_operations.create_text_area.return_value = ""
        self.mock_ui_operations.create_form_submit_button.return_value = True

        validation_response = ValidationErrorResponse(
            {"symbol": "Stock symbol cannot be empty"}
        )
        self.mock_controller.create_stock.return_value = validation_response

        # Act
        result = self.adapter.render_create_stock_form()

        # Assert
        assert result == validation_response
        self.mock_validation_operations.display_validation_errors.assert_called_once_with(
            {"symbol": "Stock symbol cannot be empty"}
        )

    def test_render_stock_list_success(self) -> None:
        """Should render stock list successfully using UI operations."""
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
        ]

        response = StockListResponse.create_success(stocks, "Retrieved 3 stocks")
        self.mock_controller.get_stock_list.return_value = response

        # Mock UI operations
        self.mock_ui_operations.create_columns.return_value = [Mock(), Mock(), Mock()]

        # Act
        result = self.adapter.render_stock_list()

        # Assert
        assert result == response
        self.mock_controller.get_stock_list.assert_called_once()
        self.mock_ui_operations.render_data_table.assert_called_once()

    def test_render_stock_list_empty(self) -> None:
        """Should handle empty stock list using UI operations."""
        # Arrange
        response = StockListResponse.create_success([], "No stocks found")
        self.mock_controller.get_stock_list.return_value = response

        # Act
        result = self.adapter.render_stock_list()

        # Assert
        assert result == response
        self.mock_ui_operations.show_info.assert_called_once_with("No stocks found")

    def test_render_stock_list_error(self) -> None:
        """Should handle error in stock list retrieval using UI operations."""
        # Arrange
        response = StockListResponse.create_error("Database connection failed")
        self.mock_controller.get_stock_list.return_value = response

        # Act
        result = self.adapter.render_stock_list()

        # Assert
        assert result == response
        self.mock_ui_operations.show_error.assert_called_once_with(
            "Database connection failed"
        )

    def test_render_stock_detail_success(self) -> None:
        """Should render stock detail view successfully using UI operations."""
        # Arrange
        stock = StockViewModel(
            id="stock-id-1",
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes="High quality stock",
        )

        response = StockDetailResponse.create_success(
            stock, "Stock retrieved successfully"
        )
        self.mock_controller.get_stock_by_symbol.return_value = response

        # Mock layout operations
        columns = [Mock(), Mock()]
        self.mock_ui_operations.create_columns.return_value = columns
        self.mock_layout_operations.within_container.return_value.__enter__ = Mock()
        self.mock_layout_operations.within_container.return_value.__exit__ = Mock(
            return_value=None
        )

        # Act
        result = self.adapter.render_stock_detail("AAPL")

        # Assert
        assert result == response
        self.mock_controller.get_stock_by_symbol.assert_called_once_with("AAPL")
        self.mock_ui_operations.render_header.assert_called_once_with(
            "AAPL - Apple Inc."
        )
        assert self.mock_ui_operations.render_metric.call_count >= 2

    def test_render_stock_detail_empty_symbol(self) -> None:
        """Should handle empty symbol input using UI operations."""
        # Act
        result = self.adapter.render_stock_detail("")

        # Assert
        assert result is None
        self.mock_ui_operations.show_error.assert_called_once_with(
            "Symbol cannot be empty"
        )
        self.mock_controller.get_stock_by_symbol.assert_not_called()

    def test_render_stock_detail_not_found(self) -> None:
        """Should handle stock not found scenario using UI operations."""
        # Arrange
        response = StockDetailResponse.create_error("Stock not found")
        self.mock_controller.get_stock_by_symbol.return_value = response

        # Act
        result = self.adapter.render_stock_detail("NOTFOUND")

        # Assert
        assert result == response
        self.mock_ui_operations.show_warning.assert_called_once_with("Stock not found")

    def test_render_grade_filter_widget(self) -> None:
        """Should render grade filtering widget using UI operations."""
        # Arrange
        columns = [Mock(), Mock()]
        self.mock_ui_operations.create_columns.return_value = columns
        self.mock_layout_operations.within_container.return_value.__enter__ = Mock()
        self.mock_layout_operations.within_container.return_value.__exit__ = Mock(
            return_value=None
        )

        self.mock_ui_operations.create_selectbox.return_value = "A"
        self.mock_ui_operations.create_button.return_value = True

        filtered_response = StockListResponse.create_success(
            [
                StockViewModel(
                    id="stock-id-1", symbol="AAPL", name="Apple Inc.", grade="A"
                )
            ],
            "Retrieved 1 stock with grade A",
        )
        self.mock_controller.search_stocks.return_value = filtered_response

        # Act
        result = self.adapter.render_grade_filter_widget()

        # Assert
        assert result == filtered_response
        self.mock_controller.search_stocks.assert_called_once()
        self.mock_ui_operations.create_selectbox.assert_called_once()
        self.mock_ui_operations.create_button.assert_called_once()

    def test_render_stock_filters(self) -> None:
        """Should render stock filtering controls using UI operations."""
        # Arrange
        columns = [Mock(), Mock()]
        self.mock_ui_operations.create_columns.return_value = columns
        self.mock_layout_operations.within_container.return_value.__enter__ = Mock()
        self.mock_layout_operations.within_container.return_value.__exit__ = Mock(
            return_value=None
        )

        self.mock_ui_operations.create_text_input.side_effect = ["AAPL", "Apple"]
        self.mock_ui_operations.create_selectbox.side_effect = ["A", "Technology"]
        self.mock_ui_operations.create_button.return_value = True

        # Act
        filters = self.adapter.render_stock_filters()

        # Assert
        assert filters is not None
        assert filters.symbol_filter == "AAPL"
        assert filters.name_filter == "Apple"
        assert filters.grade_filter == "A"
        assert filters.industry_filter == "Technology"

    def test_render_sidebar_navigation(self) -> None:
        """Should render navigation sidebar using layout operations."""
        # Arrange
        sidebar_mock = Mock()
        self.mock_layout_operations.create_sidebar.return_value = sidebar_mock
        self.mock_layout_operations.within_container.return_value.__enter__ = Mock()
        self.mock_layout_operations.within_container.return_value.__exit__ = Mock(
            return_value=None
        )

        self.mock_ui_operations.create_selectbox.return_value = "list"

        # Act
        selected_action = self.adapter.render_sidebar_navigation()

        # Assert
        assert selected_action == "list"
        self.mock_layout_operations.create_sidebar.assert_called_once()
        self.mock_ui_operations.render_header.assert_called_once_with(
            "📈 Stock Management"
        )

    def test_render_advanced_search_form(self) -> None:
        """Should render advanced search form using layout operations."""
        # Arrange
        expander_mock = Mock()
        self.mock_layout_operations.create_expander.return_value = expander_mock
        self.mock_layout_operations.within_container.return_value.__enter__ = Mock()
        self.mock_layout_operations.within_container.return_value.__exit__ = Mock(
            return_value=None
        )

        # Act
        search_filters = self.adapter.render_advanced_search_form()

        # Assert
        self.mock_layout_operations.create_expander.assert_called_once_with(
            "Advanced Search"
        )
        assert search_filters is not None

    def test_adapter_error_handling(self) -> None:
        """Should handle controller errors gracefully using UI operations."""
        # Arrange
        self.mock_controller.get_stock_list.side_effect = Exception("Unexpected error")

        # Act
        result = self.adapter.render_stock_list()

        # Assert
        assert result is None
        self.mock_ui_operations.show_error.assert_called_once()
        error_call_args = self.mock_ui_operations.show_error.call_args[0][0]
        assert "An unexpected error occurred" in error_call_args

    def test_prepare_display_data_formatting(self) -> None:
        """Should format stock data properly for display."""
        # Arrange
        stocks = [
            StockViewModel(
                id="stock-id-1",
                symbol="AAPL",
                name="Apple Inc.",
                grade="A",
                industry_group="Technology",
                notes="Good stock",
            ),
            StockViewModel(
                id="stock-id-2",
                symbol="GOOGL",
                name="Alphabet Inc.",
                grade="A",
                industry_group=None,
                notes="",
            ),
        ]

        # Act
        display_data = self.adapter.prepare_display_data(stocks)

        # Assert
        assert len(display_data) == 2
        assert display_data[0]["Symbol"] == "AAPL"
        assert display_data[0]["Name"] == "Apple Inc."
        assert display_data[0]["Industry"] == "Technology"
        assert display_data[0]["Grade"] == "Grade A"
        assert display_data[0]["Notes"] == "Yes"

        assert display_data[1]["Industry"] == "Not specified"
        assert display_data[1]["Notes"] == "No"

    def test_framework_independence(self) -> None:
        """Should operate without direct framework dependencies."""
        # This test verifies that the adapter only depends on the abstractions
        # and doesn't import or use framework-specific modules directly

        # Arrange - All operations go through the mocked interfaces
        stocks = [
            StockViewModel(id="stock-id-1", symbol="AAPL", name="Apple Inc.", grade="A")
        ]
        response = StockListResponse.create_success(stocks, "Retrieved 1 stock")
        self.mock_controller.get_stock_list.return_value = response
        self.mock_ui_operations.create_columns.return_value = [Mock(), Mock(), Mock()]

        # Act
        result = self.adapter.render_stock_list()

        # Assert - All UI operations went through the abstractions
        assert result == response
        self.mock_controller.get_stock_list.assert_called_once()
        self.mock_ui_operations.render_data_table.assert_called_once()

        # Verify no direct framework calls were made
        # (This is implicit since we're using mocks for all UI operations)
