"""
Stock page coordinator for presentation layer.

Orchestrates stock-related page flows, managing multiple controllers
and adapters to deliver complete user experiences.
"""

import logging
from typing import Any, Dict, List, Optional, Union

import streamlit as st

from src.presentation.adapters.stock_presentation_adapter import (  # type: ignore[misc]
    StockPresentationAdapter,
)
from src.presentation.adapters.streamlit_stock_adapter import StreamlitStockAdapter
from src.presentation.controllers.stock_controller import StockController
from src.presentation.view_models.stock_view_models import (  # type: ignore[misc]
    CreateStockResponse,
    StockDetailResponse,
    StockViewModel,
    ValidationErrorResponse,
)

logger = logging.getLogger(__name__)  # type: ignore[misc]


class StockPageCoordinator:
    """
    Coordinates stock-related page flows and user experiences.

    Manages multiple components to deliver complete page functionality,
    handling navigation, state management, and user feedback.
    """

    def __init__(
        self,
        controller: StockController,
        adapter: StreamlitStockAdapter,
        presentation_adapter: Optional[StockPresentationAdapter] = None,
    ):
        """
        Initialize coordinator with controller and adapters.

        Args:
            controller: Stock controller for business logic
            adapter: Streamlit adapter for UI rendering (legacy)  # type: ignore[misc]
            presentation_adapter: Framework-agnostic presentation adapter (preferred)  # type: ignore[misc]
        """
        self.controller = controller
        self.adapter = adapter
        self.presentation_adapter = presentation_adapter
        self.initialize_page_state()  # type: ignore[misc]

    def get_active_adapter(self) -> Any:
        """
        Get the active adapter to use for rendering.

        Prefers the framework-agnostic presentation adapter if available,
        falls back to the legacy Streamlit adapter.

        Returns:
            The adapter to use for UI operations
        """
        return self.presentation_adapter if self.presentation_adapter else self.adapter

    def render_stock_dashboard(self) -> Optional[Dict[str, Any]]:
        """
        Render complete stock dashboard with tabs and metrics.

        Returns:
            Dashboard render results
        """
        try:
            st.header("📈 Stock Dashboard")  # type: ignore[misc]

            # Get stock data for metrics
            stock_response = self.controller.get_stock_list()  # type: ignore[misc]

            # Show metrics if we have data
            if stock_response.success and stock_response.stocks:
                metrics = self.calculate_stock_metrics(stock_response.stocks)  # type: ignore[misc]
                self.render_stock_metrics(metrics)  # type: ignore[misc]

            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["All Stocks", "By Grade", "Add Stock"])

            results = {}

            with tab1:
                st.subheader("📋 All Stocks")
                results["all_stocks"] = self.adapter.render_stock_list()  # type: ignore[misc]

            with tab2:
                st.subheader("🎯 Filter by Grade")
                results["grade_filter"] = self.adapter.render_grade_filter_widget()  # type: ignore[misc]

            with tab3:
                st.subheader("➕ Add New Stock")
                create_result = self.adapter.render_create_stock_form(
                    refresh_on_success=True
                )  # type: ignore[misc]
                if create_result:
                    results["create_stock"] = self._handle_create_stock_result(
                        create_result
                    )  # type: ignore[misc]

            return results  # type: ignore[misc] - Temporary UI framework dict

        except Exception as e:
            logger.error(f"Error rendering stock dashboard: {e}")  # type: ignore[misc]
            st.error("An unexpected error occurred while loading the dashboard")
            return None

    def render_stock_management_page(self) -> Optional[Any]:
        """
        Render stock management page with sidebar navigation.

        Returns:
            Page render result based on selected action
        """
        try:
            # Render sidebar navigation (use legacy adapter for Streamlit-specific UI)  # type: ignore[misc]
            selected_action = self.adapter.render_sidebar_navigation()  # type: ignore[misc]

            # Route to appropriate view based on selection
            if selected_action == "list":
                st.header("📋 All Stocks")
                return self.get_active_adapter().render_stock_list(show_metrics=True)  # type: ignore[misc]

            if selected_action == "create":
                st.header("➕ Add New Stock")
                create_result = self.get_active_adapter().render_create_stock_form()  # type: ignore[misc]
                if create_result:
                    return self._handle_create_stock_result(create_result)  # type: ignore[misc]
                return None

            if selected_action == "search":
                return self._handle_search_action()

            # Default to stock list
            return self.get_active_adapter().render_stock_list()  # type: ignore[misc]

        except Exception as e:
            logger.error(f"Error rendering stock management page: {e}")  # type: ignore[misc]
            st.error("An unexpected error occurred while loading the page")
            return None

    def _handle_search_action(self) -> Optional[Any]:
        """Handle search action with reduced nesting complexity."""
        st.header("🔍 Search Stocks")
        search_result = self.get_active_adapter().render_advanced_search_form()  # type: ignore[misc]

        if not search_result or not search_result.has_filters:
            return search_result

        search_response = self.controller.search_stocks(search_result)  # type: ignore[misc]
        self._process_search_response(search_response)
        return search_result

    def _process_search_response(self, search_response: Any) -> None:
        """Process search response with simplified control flow."""
        if isinstance(search_response, ValidationErrorResponse):
            self.handle_validation_errors(search_response)  # type: ignore[misc]
            return

        if not search_response.success:
            st.error(search_response.message)
            return

        st.success(search_response.message)
        if search_response.stocks:
            self.get_active_adapter().render_stock_dataframe_with_data(
                search_response.stocks
            )  # type: ignore[misc]
        else:
            st.info("No stocks found matching your criteria")

    def _is_valid_stock_detail_response(self, response: Any) -> bool:
        """Check if response is a valid stock detail response."""
        return (
            response is not None
            and not isinstance(response, ValidationErrorResponse)
            and response.success
            and response.stock is not None
        )

    def render_stock_detail_page(
        self, symbol: str
    ) -> Union[StockDetailResponse, ValidationErrorResponse, None]:
        """
        Render detailed stock information page.

        Args:
            symbol: Stock symbol to display

        Returns:
            Stock detail response
        """
        try:
            st.header("📊 Stock Details")

            response = self.adapter.render_stock_detail(symbol)  # type: ignore[misc]

            if self._is_valid_stock_detail_response(response):
                # Add additional detail sections
                self._render_stock_detail_sections(response.stock)  # type: ignore[misc]

            return response

        except Exception as e:
            logger.error(f"Error rendering stock detail page: {e}")  # type: ignore[misc]
            st.error("An unexpected error occurred while loading stock details")
            return None

    def _handle_create_stock_result(
        self, result: Union[CreateStockResponse, ValidationErrorResponse]
    ) -> Any:
        """Handle stock creation result with appropriate user feedback."""
        if isinstance(result, ValidationErrorResponse):
            return self.handle_validation_errors(result)  # type: ignore[misc]
        if result.success:
            return self.handle_stock_creation_success(result)  # type: ignore[misc]
        return self.handle_stock_creation_error(result)  # type: ignore[misc]

    def handle_stock_creation_success(
        self, response: CreateStockResponse
    ) -> CreateStockResponse:
        """Handle successful stock creation with celebration."""
        st.success(f"✅ Stock {response.symbol} created successfully!")
        st.balloons()
        return response

    def handle_stock_creation_error(
        self, response: CreateStockResponse
    ) -> CreateStockResponse:
        """Handle stock creation errors."""
        st.error(f"❌ {response.message}")
        return response

    def handle_validation_errors(
        self, response: ValidationErrorResponse
    ) -> ValidationErrorResponse:
        """Handle validation errors with detailed feedback."""
        error_message = "⚠️ Please fix the following errors:\n\n"
        for field_error in response.field_errors:
            error_message += f"• {field_error}\n"

        st.warning(error_message)
        return response

    def calculate_stock_metrics(self, stocks: List[StockViewModel]) -> Dict[str, Any]:
        """Calculate summary metrics for stock list."""
        total_stocks = len(stocks)  # type: ignore[misc]

        grade_counts = {"A": 0, "B": 0, "C": 0}
        for stock in stocks:
            grade_value = stock.grade if stock.grade else "Ungraded"
            if grade_value in grade_counts:
                grade_counts[grade_value] += 1

        high_grade_percentage = (
            (grade_counts["A"] / total_stocks * 100) if total_stocks > 0 else 0
        )  # type: ignore[misc]

        return {
            "total_stocks": total_stocks,
            "grade_a_count": grade_counts["A"],
            "grade_b_count": grade_counts["B"],
            "grade_c_count": grade_counts["C"],
            "high_grade_percentage": high_grade_percentage,
        }

    def render_stock_metrics(self, metrics: Dict[str, Any]) -> None:
        """Render stock metrics display."""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Stocks", metrics["total_stocks"])

        with col2:
            st.metric("Grade A", metrics["grade_a_count"])

        with col3:
            st.metric("Grade B", metrics["grade_b_count"])

        with col4:
            st.metric("High Grade %", f"{metrics['high_grade_percentage']:.1f}%")

    def _render_stock_detail_sections(self, stock: StockViewModel) -> None:
        """Render additional sections for stock detail view."""
        try:
            # Additional information section
            with st.expander("📋 Additional Information", expanded=True):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Stock ID:** {stock.id}")  # type: ignore[misc]
                    st.write(f"**Display Name:** {stock.display_name}")  # type: ignore[misc]

                with col2:
                    st.write(
                        f"**High Grade:** {'Yes' if stock.is_high_grade else 'No'}"
                    )  # type: ignore[misc]
                    st.write(f"**Has Notes:** {'Yes' if stock.has_notes else 'No'}")  # type: ignore[misc]

            # Notes section if available
            if stock.has_notes:
                with st.expander("📝 Notes", expanded=False):
                    st.write(stock.notes.value)  # type: ignore[misc]

        except Exception as e:
            logger.error(f"Error rendering stock detail sections: {e}")  # type: ignore[misc]

    def initialize_page_state(self) -> None:
        """Initialize page-level session state."""
        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"

        if "last_action" not in st.session_state:
            st.session_state.last_action = None

    def handle_page_navigation(self) -> Optional[str]:
        """Handle navigation between page sections."""
        # Check for query parameters or session state for navigation
        if hasattr(st, "query_params"):
            symbol = st.query_params.get("symbol")  # type: ignore[misc]
            if symbol:
                return symbol

        return None

    def handle_post_action_refresh(
        self, response: Union[CreateStockResponse, Any]
    ) -> None:
        """Handle page refresh after successful actions."""
        if hasattr(response, "success") and response.success:
            st.rerun()

    def render_stock_page(self) -> Optional[Any]:
        """
        Render the main stock page with management interface.

        This is the primary entry point for the stock management section,
        providing a comprehensive interface for stock operations.

        Returns:
            Page render result
        """
        try:
            # Use the stock management page as the primary interface
            return self.render_stock_management_page()  # type: ignore[misc]

        except Exception as e:
            logger.error(f"Error rendering stock page: {e}")  # type: ignore[misc]
            st.error("An unexpected error occurred while loading the stock page")
            return None

    def execute_create_and_view_workflow(self, symbol: str) -> Optional[Any]:
        """Execute create stock followed by view detail workflow."""
        try:
            # This would be called after successful creation
            # to immediately show the created stock details
            return self.render_stock_detail_page(symbol)  # type: ignore[misc]

        except Exception as e:
            logger.error(f"Error in create-and-view workflow: {e}")  # type: ignore[misc]
            return None
