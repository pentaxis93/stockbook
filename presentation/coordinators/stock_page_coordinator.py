"""
Stock page coordinator for presentation layer.

Orchestrates stock-related page flows, managing multiple controllers
and adapters to deliver complete user experiences.
"""

import streamlit as st
from typing import Dict, Any, List, Optional, Union
import logging

from presentation.controllers.stock_controller import StockController
from presentation.adapters.streamlit_stock_adapter import StreamlitStockAdapter
from presentation.view_models.stock_view_models import (
    StockListResponse, CreateStockResponse, StockDetailResponse,
    ValidationErrorResponse, StockViewModel
)

logger = logging.getLogger(__name__)


class StockPageCoordinator:
    """
    Coordinates stock-related page flows and user experiences.
    
    Manages multiple components to deliver complete page functionality,
    handling navigation, state management, and user feedback.
    """
    
    def __init__(self, controller: StockController, adapter: StreamlitStockAdapter):
        """
        Initialize coordinator with controller and adapter.
        
        Args:
            controller: Stock controller for business logic
            adapter: Streamlit adapter for UI rendering
        """
        self.controller = controller
        self.adapter = adapter
        self._initialize_page_state()
    
    def render_stock_dashboard(self) -> Optional[Dict[str, Any]]:
        """
        Render complete stock dashboard with tabs and metrics.
        
        Returns:
            Dashboard render results
        """
        try:
            st.header("📈 Stock Dashboard")
            
            # Get stock data for metrics
            stock_response = self.controller.get_stock_list()
            
            # Show metrics if we have data
            if stock_response.success and stock_response.stocks:
                metrics = self._calculate_stock_metrics(stock_response.stocks)
                self._render_stock_metrics(metrics)
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["All Stocks", "By Grade", "Add Stock"])
            
            results = {}
            
            with tab1:
                st.subheader("📋 All Stocks")
                results["all_stocks"] = self.adapter.render_stock_list()
            
            with tab2:
                st.subheader("🎯 Filter by Grade")
                results["grade_filter"] = self.adapter.render_grade_filter_widget()
            
            with tab3:
                st.subheader("➕ Add New Stock")
                create_result = self.adapter.render_create_stock_form(refresh_on_success=True)
                if create_result:
                    results["create_stock"] = self._handle_create_stock_result(create_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error rendering stock dashboard: {e}")
            st.error("An unexpected error occurred while loading the dashboard")
            return None
    
    def render_stock_management_page(self) -> Optional[Any]:
        """
        Render stock management page with sidebar navigation.
        
        Returns:
            Page render result based on selected action
        """
        try:
            # Render sidebar navigation
            selected_action = self.adapter.render_sidebar_navigation()
            
            # Route to appropriate view based on selection
            if selected_action == "list":
                st.header("📋 All Stocks")
                return self.adapter.render_stock_list(show_metrics=True)
            
            elif selected_action == "create":
                st.header("➕ Add New Stock")
                create_result = self.adapter.render_create_stock_form()
                if create_result:
                    return self._handle_create_stock_result(create_result)
                return None
            
            elif selected_action == "search":
                st.header("🔍 Search Stocks")
                search_result = self.adapter.render_advanced_search_form()
                if search_result:
                    # TODO: Implement search results display
                    st.info("Search functionality coming soon!")
                return search_result
            
            else:
                # Default to stock list
                return self.adapter.render_stock_list()
                
        except Exception as e:
            logger.error(f"Error rendering stock management page: {e}")
            st.error("An unexpected error occurred while loading the page")
            return None
    
    def render_stock_detail_page(self, symbol: str) -> Optional[StockDetailResponse]:
        """
        Render detailed stock information page.
        
        Args:
            symbol: Stock symbol to display
            
        Returns:
            Stock detail response
        """
        try:
            st.header("📊 Stock Details")
            
            response = self.adapter.render_stock_detail(symbol)
            
            if response and response.success:
                # Add additional detail sections
                self._render_stock_detail_sections(response.stock)
            
            return response
            
        except Exception as e:
            logger.error(f"Error rendering stock detail page: {e}")
            st.error("An unexpected error occurred while loading stock details")
            return None
    
    def _handle_create_stock_result(self, result: Union[CreateStockResponse, ValidationErrorResponse]) -> Any:
        """Handle stock creation result with appropriate user feedback."""
        if isinstance(result, ValidationErrorResponse):
            return self._handle_validation_errors(result)
        elif result.success:
            return self._handle_stock_creation_success(result)
        else:
            return self._handle_stock_creation_error(result)
    
    def _handle_stock_creation_success(self, response: CreateStockResponse) -> CreateStockResponse:
        """Handle successful stock creation with celebration."""
        st.success(f"✅ Stock {response.symbol} created successfully!")
        st.balloons()
        return response
    
    def _handle_stock_creation_error(self, response: CreateStockResponse) -> CreateStockResponse:
        """Handle stock creation errors."""
        st.error(f"❌ {response.message}")
        return response
    
    def _handle_validation_errors(self, response: ValidationErrorResponse) -> ValidationErrorResponse:
        """Handle validation errors with detailed feedback."""
        error_message = "⚠️ Please fix the following errors:\n\n"
        for field_error in response.field_errors:
            error_message += f"• {field_error}\n"
        
        st.warning(error_message)
        return response
    
    def _calculate_stock_metrics(self, stocks: List[StockViewModel]) -> Dict[str, Any]:
        """Calculate summary metrics for stock list."""
        total_stocks = len(stocks)
        
        grade_counts = {"A": 0, "B": 0, "C": 0}
        for stock in stocks:
            if stock.grade in grade_counts:
                grade_counts[stock.grade] += 1
        
        high_grade_percentage = (grade_counts["A"] / total_stocks * 100) if total_stocks > 0 else 0
        
        return {
            "total_stocks": total_stocks,
            "grade_a_count": grade_counts["A"],
            "grade_b_count": grade_counts["B"],
            "grade_c_count": grade_counts["C"],
            "high_grade_percentage": high_grade_percentage
        }
    
    def _render_stock_metrics(self, metrics: Dict[str, Any]) -> None:
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
                    st.write(f"**Stock ID:** {stock.id}")
                    st.write(f"**Display Name:** {stock.display_name}")
                
                with col2:
                    st.write(f"**High Grade:** {'Yes' if stock.is_high_grade else 'No'}")
                    st.write(f"**Has Notes:** {'Yes' if stock.has_notes else 'No'}")
            
            # Notes section if available
            if stock.has_notes:
                with st.expander("📝 Notes", expanded=False):
                    st.write(stock.notes)
                    
        except Exception as e:
            logger.error(f"Error rendering stock detail sections: {e}")
    
    def _initialize_page_state(self) -> None:
        """Initialize page-level session state."""
        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"
        
        if "last_action" not in st.session_state:
            st.session_state.last_action = None
    
    def _handle_page_navigation(self) -> Optional[str]:
        """Handle navigation between page sections."""
        # Check for query parameters or session state for navigation
        if hasattr(st, 'query_params'):
            symbol = st.query_params.get('symbol')
            if symbol:
                return symbol
        
        return None
    
    def _handle_post_action_refresh(self, response: Union[CreateStockResponse, Any]) -> None:
        """Handle page refresh after successful actions."""
        if hasattr(response, 'success') and response.success:
            st.rerun()
    
    def _execute_create_and_view_workflow(self, symbol: str) -> Optional[Any]:
        """Execute create stock followed by view detail workflow."""
        try:
            # This would be called after successful creation
            # to immediately show the created stock details
            return self.render_stock_detail_page(symbol)
            
        except Exception as e:
            logger.error(f"Error in create-and-view workflow: {e}")
            return None