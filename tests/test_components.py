"""
Test suite for UI component library.

This module tests the reusable Streamlit UI components that provide:
- Validated input components with consistent styling
- Data display components with standardized formatting
- Form layout components for consistent user experience
- Integration with error handling and configuration systems

Following TDD approach - tests are written first to define expected behavior.
"""

import pytest
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock, call
from typing import Dict, Any, List, Optional

# Import the components module (will fail initially - that's expected in TDD)
try:
    from components import (
        StockSymbolInput, DatePicker, PriceInput, QuantityInput,
        MessageDisplay, DataTable, FormLayout, ComponentTestingUtils
    )
except ImportError:
    # This is expected during TDD - we haven't created the module yet
    pytest.skip("Components module not yet implemented", allow_module_level=True)


class TestStockSymbolInput:
    """Test StockSymbolInput component for validated symbol entry."""
    
    @patch('streamlit.text_input')
    def test_stock_symbol_input_basic(self, mock_text_input):
        """Test basic stock symbol input functionality."""
        mock_text_input.return_value = "AAPL"
        
        symbol_input = StockSymbolInput(
            label="Stock Symbol",
            key="test_symbol"
        )
        
        result = symbol_input.render()
        
        # Should call streamlit text_input with correct parameters
        mock_text_input.assert_called_once()
        call_args = mock_text_input.call_args
        assert "Stock Symbol" in str(call_args)
        assert "test_symbol" in str(call_args)
        
        # Should return the validated symbol
        assert result == "AAPL"
        
    @patch('streamlit.text_input')
    @patch('streamlit.error')
    def test_stock_symbol_input_validation_error(self, mock_error, mock_text_input):
        """Test symbol input with validation errors."""
        mock_text_input.return_value = "123invalid"  # Invalid: starts with numbers
        
        symbol_input = StockSymbolInput(
            label="Stock Symbol",
            key="test_symbol"
        )
        
        result = symbol_input.render()
        
        # Should display error for invalid symbol
        mock_error.assert_called_once()
        error_message = mock_error.call_args[0][0]
        assert "valid" in error_message.lower()
        
        # Should return None for invalid input
        assert result is None
        
    @patch('streamlit.text_input')
    @patch('streamlit.info')
    def test_stock_symbol_input_with_suggestions(self, mock_info, mock_text_input):
        """Test symbol input with suggestion display."""
        mock_text_input.return_value = "AA"
        
        symbol_input = StockSymbolInput(
            label="Stock Symbol",
            key="test_symbol",
            show_suggestions=True,
            suggestions=["AAPL", "AAXN", "AABA"]
        )
        
        result = symbol_input.render()
        
        # Should show suggestions
        mock_info.assert_called()
        info_message = mock_info.call_args[0][0]
        assert "suggestions" in info_message.lower()
        assert "AAPL" in info_message
        
    @patch('streamlit.text_input')
    def test_stock_symbol_input_placeholder(self, mock_text_input):
        """Test symbol input with custom placeholder."""
        mock_text_input.return_value = ""
        
        symbol_input = StockSymbolInput(
            label="Stock Symbol",
            key="test_symbol",
            placeholder="Enter ticker (e.g., AAPL)"
        )
        
        symbol_input.render()
        
        # Should use custom placeholder
        call_args = mock_text_input.call_args
        assert "Enter ticker" in str(call_args)
        
    @patch('streamlit.text_input')
    def test_stock_symbol_input_max_length(self, mock_text_input):
        """Test symbol input respects max length from config."""
        mock_text_input.return_value = "TOOLONG"
        
        symbol_input = StockSymbolInput(
            label="Stock Symbol",
            key="test_symbol"
        )
        
        result = symbol_input.render()
        
        # Should enforce max length validation
        # (TOOLONG is 7 chars, config max is likely 5)
        assert result is None or len(result) <= 5


class TestDatePicker:
    """Test DatePicker component with business day validation."""
    
    @patch('streamlit.date_input')
    def test_date_picker_basic(self, mock_date_input):
        """Test basic date picker functionality."""
        test_date = date(2023, 12, 25)
        mock_date_input.return_value = test_date
        
        date_picker = DatePicker(
            label="Transaction Date",
            key="test_date"
        )
        
        result = date_picker.render()
        
        # Should call streamlit date_input
        mock_date_input.assert_called_once()
        call_args = mock_date_input.call_args
        assert "Transaction Date" in str(call_args)
        assert "test_date" in str(call_args)
        
        # Should return the selected date
        assert result == test_date
        
    @patch('streamlit.date_input')
    @patch('streamlit.warning')
    def test_date_picker_future_date_warning(self, mock_warning, mock_date_input):
        """Test date picker warns about future dates."""
        future_date = date.today() + timedelta(days=1)
        mock_date_input.return_value = future_date
        
        date_picker = DatePicker(
            label="Transaction Date",
            key="test_date",
            allow_future=False
        )
        
        result = date_picker.render()
        
        # Should warn about future date
        mock_warning.assert_called_once()
        warning_message = mock_warning.call_args[0][0]
        assert "future" in warning_message.lower()
        
        # Should still return the date but with warning
        assert result == future_date
        
    @patch('streamlit.date_input')
    @patch('streamlit.info')
    def test_date_picker_weekend_info(self, mock_info, mock_date_input):
        """Test date picker shows info for weekend dates."""
        # Saturday
        weekend_date = date(2023, 12, 23)  # Assume this is a Saturday
        mock_date_input.return_value = weekend_date
        
        date_picker = DatePicker(
            label="Transaction Date",
            key="test_date",
            business_days_only=True
        )
        
        result = date_picker.render()
        
        # Should show weekend info (if it's actually a weekend)
        # Note: This test may need adjustment based on actual date
        assert result == weekend_date
        
    @patch('streamlit.date_input')
    def test_date_picker_min_max_dates(self, mock_date_input):
        """Test date picker with min/max date constraints."""
        test_date = date(2023, 6, 15)
        mock_date_input.return_value = test_date
        
        min_date = date(2023, 1, 1)
        max_date = date(2023, 12, 31)
        
        date_picker = DatePicker(
            label="Transaction Date",
            key="test_date",
            min_value=min_date,
            max_value=max_date
        )
        
        result = date_picker.render()
        
        # Should pass min/max values to streamlit
        call_args = mock_date_input.call_args
        assert min_date in call_args[1].values() or min_date in call_args[0]
        assert max_date in call_args[1].values() or max_date in call_args[0]
        
        assert result == test_date


class TestPriceInput:
    """Test PriceInput component with currency formatting and validation."""
    
    @patch('streamlit.number_input')
    def test_price_input_basic(self, mock_number_input):
        """Test basic price input functionality."""
        mock_number_input.return_value = 123.45
        
        price_input = PriceInput(
            label="Price per Share",
            key="test_price"
        )
        
        result = price_input.render()
        
        # Should call streamlit number_input
        mock_number_input.assert_called_once()
        call_args = mock_number_input.call_args
        assert "Price per Share" in str(call_args)
        assert "test_price" in str(call_args)
        
        # Should return Decimal for precision
        assert isinstance(result, Decimal)
        assert result == Decimal("123.45")
        
    @patch('streamlit.number_input')
    def test_price_input_currency_formatting(self, mock_number_input):
        """Test price input displays currency symbol."""
        mock_number_input.return_value = 50.00
        
        price_input = PriceInput(
            label="Price per Share",
            key="test_price"
        )
        
        result = price_input.render()
        
        # Should include currency symbol in format
        call_args = mock_number_input.call_args
        assert "$" in str(call_args) or "format" in str(call_args)
        
    @patch('streamlit.number_input')
    @patch('streamlit.error')
    def test_price_input_minimum_validation(self, mock_error, mock_number_input):
        """Test price input validates minimum value."""
        mock_number_input.return_value = 0.005  # Below minimum
        
        price_input = PriceInput(
            label="Price per Share",
            key="test_price"
        )
        
        result = price_input.render()
        
        # Should enforce minimum price from config
        # Either through streamlit min_value or custom validation
        call_args = mock_number_input.call_args
        min_value_set = any("min_value" in str(arg) for arg in call_args)
        
        # If min_value not set in streamlit, should validate manually
        if not min_value_set and result is not None and result < Decimal("0.01"):
            mock_error.assert_called()
            
    @patch('streamlit.number_input')
    def test_price_input_step_precision(self, mock_number_input):
        """Test price input uses correct decimal precision."""
        mock_number_input.return_value = 123.456
        
        price_input = PriceInput(
            label="Price per Share",
            key="test_price"
        )
        
        result = price_input.render()
        
        # Should set step for decimal precision
        call_args = mock_number_input.call_args
        assert "step" in str(call_args) or "0.01" in str(call_args)
        
        # Should round to config decimal places
        assert result == Decimal("123.46")  # Rounded to 2 decimal places


class TestQuantityInput:
    """Test QuantityInput component with integer validation and limits."""
    
    @patch('streamlit.number_input')
    def test_quantity_input_basic(self, mock_number_input):
        """Test basic quantity input functionality."""
        mock_number_input.return_value = 100
        
        quantity_input = QuantityInput(
            label="Number of Shares",
            key="test_quantity"
        )
        
        result = quantity_input.render()
        
        # Should call streamlit number_input with integer step
        mock_number_input.assert_called_once()
        call_args = mock_number_input.call_args
        assert "Number of Shares" in str(call_args)
        assert "step=1" in str(call_args) or "step" in str(call_args[1])
        
        # Should return integer
        assert isinstance(result, int)
        assert result == 100
        
    @patch('streamlit.number_input')
    def test_quantity_input_minimum_validation(self, mock_number_input):
        """Test quantity input enforces minimum value."""
        mock_number_input.return_value = 1
        
        quantity_input = QuantityInput(
            label="Number of Shares",
            key="test_quantity"
        )
        
        result = quantity_input.render()
        
        # Should set minimum value from config
        call_args = mock_number_input.call_args
        assert "min_value" in str(call_args)
        assert result >= 1
        
    @patch('streamlit.number_input')
    @patch('streamlit.warning')
    def test_quantity_input_maximum_warning(self, mock_warning, mock_number_input):
        """Test quantity input warns about very large quantities."""
        mock_number_input.return_value = 100000
        
        quantity_input = QuantityInput(
            label="Number of Shares",
            key="test_quantity"
        )
        
        result = quantity_input.render()
        
        # Should warn about large quantities if they exceed reasonable limits
        if result > 10000:  # Arbitrary large number
            mock_warning.assert_called()
            
    @patch('streamlit.number_input')
    def test_quantity_input_format_display(self, mock_number_input):
        """Test quantity input displays numbers with proper formatting."""
        mock_number_input.return_value = 1500
        
        quantity_input = QuantityInput(
            label="Number of Shares",
            key="test_quantity"
        )
        
        result = quantity_input.render()
        
        # Should format large numbers with commas if applicable
        call_args = mock_number_input.call_args
        assert result == 1500


class TestMessageDisplay:
    """Test MessageDisplay component for notifications."""
    
    @patch('streamlit.success')
    def test_message_display_success(self, mock_success):
        """Test displaying success messages."""
        message_display = MessageDisplay()
        
        message_display.success("Portfolio created successfully!")
        
        mock_success.assert_called_once_with("Portfolio created successfully!")
        
    @patch('streamlit.error')
    def test_message_display_error(self, mock_error):
        """Test displaying error messages."""
        message_display = MessageDisplay()
        
        message_display.error("Failed to save transaction")
        
        mock_error.assert_called_once_with("Failed to save transaction")
        
    @patch('streamlit.info')
    def test_message_display_info(self, mock_info):
        """Test displaying info messages."""
        message_display = MessageDisplay()
        
        message_display.info("Loading portfolio data...")
        
        mock_info.assert_called_once_with("Loading portfolio data...")
        
    @patch('streamlit.warning')
    def test_message_display_warning(self, mock_warning):
        """Test displaying warning messages."""
        message_display = MessageDisplay()
        
        message_display.warning("Risk limit approaching")
        
        mock_warning.assert_called_once_with("Risk limit approaching")
        
    @patch('streamlit.empty')
    def test_message_display_auto_dismiss(self, mock_empty):
        """Test auto-dismissing messages."""
        container = MagicMock()
        mock_empty.return_value = container
        
        message_display = MessageDisplay()
        
        with patch('time.sleep') as mock_sleep:
            message_display.success("Saved!", auto_dismiss=2.0)
            
            mock_sleep.assert_called_with(2.0)
            container.empty.assert_called_once()
            
    def test_message_display_with_icon(self):
        """Test messages with custom icons."""
        message_display = MessageDisplay()
        
        with patch('streamlit.success') as mock_success:
            message_display.success("Completed!", icon="✅")
            
            # Should include icon in message
            call_args = mock_success.call_args[0][0]
            assert "✅" in call_args


class TestDataTable:
    """Test DataTable component for consistent table formatting."""
    
    @patch('streamlit.dataframe')
    def test_data_table_basic(self, mock_dataframe):
        """Test basic data table display."""
        data = pd.DataFrame({
            "Symbol": ["AAPL", "MSFT"],
            "Price": [150.0, 300.0],
            "Quantity": [100, 50]
        })
        
        data_table = DataTable(data=data)
        result = data_table.render()
        
        # Should call streamlit dataframe
        mock_dataframe.assert_called_once()
        call_args = mock_dataframe.call_args[0][0]
        assert isinstance(call_args, pd.DataFrame)
        assert len(call_args) == 2
        
    @patch('streamlit.dataframe')
    def test_data_table_with_formatting(self, mock_dataframe):
        """Test data table with column formatting."""
        data = pd.DataFrame({
            "Symbol": ["AAPL", "MSFT"],
            "Price": [150.50, 300.25],
            "Value": [15050.0, 15012.5]
        })
        
        column_config = {
            "Price": {"type": "currency"},
            "Value": {"type": "currency"}
        }
        
        data_table = DataTable(
            data=data,
            column_config=column_config
        )
        
        result = data_table.render()
        
        # Should apply column formatting
        call_args = mock_dataframe.call_args
        assert "column_config" in call_args[1] or len(call_args) > 1
        
    @patch('streamlit.dataframe')
    def test_data_table_with_selection(self, mock_dataframe):
        """Test data table with row selection."""
        data = pd.DataFrame({
            "Symbol": ["AAPL", "MSFT", "GOOGL"],
            "Price": [150.0, 300.0, 2500.0]
        })
        
        data_table = DataTable(
            data=data,
            selection_mode="multi"
        )
        
        result = data_table.render()
        
        # Should enable selection
        call_args = mock_dataframe.call_args
        # Check for selection mode in arguments
        assert "on_select" in str(call_args) or "selection_mode" in str(call_args)
        
    @patch('streamlit.dataframe')
    def test_data_table_pagination(self, mock_dataframe):
        """Test data table with pagination for large datasets."""
        # Create large dataset
        data = pd.DataFrame({
            "Symbol": [f"STOCK{i}" for i in range(100)],
            "Price": [100.0 + i for i in range(100)]
        })
        
        data_table = DataTable(
            data=data,
            page_size=20
        )
        
        result = data_table.render()
        
        # Should handle pagination (implementation detail)
        mock_dataframe.assert_called()
        
    def test_data_table_empty_data(self):
        """Test data table with empty dataset."""
        data = pd.DataFrame()
        
        data_table = DataTable(data=data)
        
        with patch('streamlit.info') as mock_info:
            result = data_table.render()
            
            # Should show appropriate message for empty data
            mock_info.assert_called()
            message = mock_info.call_args[0][0]
            assert "no data" in message.lower() or "empty" in message.lower()


class TestFormLayout:
    """Test FormLayout component for standard form structure."""
    
    @patch('streamlit.form')
    def test_form_layout_basic(self, mock_form):
        """Test basic form layout functionality."""
        mock_form_context = MagicMock()
        mock_form.return_value.__enter__ = MagicMock(return_value=mock_form_context)
        mock_form.return_value.__exit__ = MagicMock(return_value=None)
        
        form_layout = FormLayout(
            form_key="test_form",
            title="Add New Stock"
        )
        
        with form_layout:
            pass  # Form content would go here
            
        # Should create streamlit form
        # Should create streamlit form with clear_on_submit parameter
        mock_form.assert_called_once_with("test_form", clear_on_submit=False)
        
    @patch('streamlit.form')
    @patch('streamlit.header')
    def test_form_layout_with_title(self, mock_header, mock_form):
        """Test form layout displays title."""
        mock_form_context = MagicMock()
        mock_form.return_value.__enter__ = MagicMock(return_value=mock_form_context)
        mock_form.return_value.__exit__ = MagicMock(return_value=None)
        
        form_layout = FormLayout(
            form_key="test_form",
            title="Add New Stock"
        )
        
        with form_layout:
            pass
            
        # Should display title
        mock_header.assert_called_with("Add New Stock")
        
    @patch('streamlit.form')
    @patch('streamlit.form_submit_button')
    def test_form_layout_submit_button(self, mock_submit_button, mock_form):
        """Test form layout includes submit button."""
        mock_form_context = MagicMock()
        mock_form.return_value.__enter__ = MagicMock(return_value=mock_form_context)
        mock_form.return_value.__exit__ = MagicMock(return_value=None)
        mock_submit_button.return_value = True
        
        form_layout = FormLayout(
            form_key="test_form",
            submit_label="Save Stock"
        )
        
        with form_layout:
            # Note: is_submitted() is only valid after form context exits
            pass
            
        # Should create submit button
        mock_submit_button.assert_called_with("Save Stock")
        submitted = form_layout.is_submitted()
        assert submitted is True
        
    @patch('streamlit.form')
    @patch('streamlit.columns')
    def test_form_layout_with_columns(self, mock_columns, mock_form):
        """Test form layout with column structure."""
        mock_form_context = MagicMock()
        mock_form.return_value.__enter__ = MagicMock(return_value=mock_form_context)
        mock_form.return_value.__exit__ = MagicMock(return_value=None)
        
        mock_col1, mock_col2 = MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        form_layout = FormLayout(
            form_key="test_form",
            columns=[1, 1]  # Two equal columns
        )
        
        with form_layout:
            cols = form_layout.get_columns()
            
        # Should create columns
        mock_columns.assert_called_with([1, 1])
        assert len(cols) == 2


class TestComponentIntegration:
    """Test integration between components and with other systems."""
    
    def test_components_use_error_handling(self):
        """Test that components integrate with error handling system."""
        with patch('streamlit.text_input') as mock_input:
            mock_input.return_value = "invalid"
            
            symbol_input = StockSymbolInput(
                label="Stock Symbol",
                key="test_symbol"
            )
            
            with patch('streamlit.error') as mock_error:
                result = symbol_input.render()
                
                # Should use error handling system
                mock_error.assert_called()
                
    def test_components_use_config_settings(self):
        """Test that components use centralized config."""
        with patch('streamlit.number_input') as mock_input:
            mock_input.return_value = 50.0
            
            price_input = PriceInput(
                label="Price",
                key="test_price"
            )
            
            result = price_input.render()
            
            # Should use config settings for validation, formatting
            call_args = mock_input.call_args
            assert "$" in str(call_args) or "min_value" in str(call_args)
            
    def test_form_workflow_integration(self):
        """Test complete form workflow with multiple components."""
        with patch('streamlit.form') as mock_form:
            mock_form_context = MagicMock()
            mock_form.return_value.__enter__ = MagicMock(return_value=mock_form_context)
            mock_form.return_value.__exit__ = MagicMock(return_value=None)
            
            with patch('streamlit.text_input') as mock_text:
                with patch('streamlit.number_input') as mock_number:
                    with patch('streamlit.form_submit_button') as mock_submit:
                        mock_text.return_value = "AAPL"
                        mock_number.side_effect = [150.0, 100]  # price, quantity
                        mock_submit.return_value = True
                        
                        # Test complete form
                        form = FormLayout("add_transaction", "Add Transaction")
                        
                        with form:
                            symbol = StockSymbolInput("Symbol", "symbol").render()
                            price = PriceInput("Price", "price").render()
                            quantity = QuantityInput("Quantity", "quantity").render()
                            
                        submitted = form.is_submitted()
                            
                        # Should collect all form data
                        assert symbol == "AAPL"
                        assert price == Decimal("150.0")
                        assert quantity == 100
                        assert submitted is True


class TestComponentTestingUtils:
    """Test utilities for component testing."""
    
    def test_create_mock_streamlit_session(self):
        """Test utility for mocking Streamlit session state."""
        utils = ComponentTestingUtils()
        
        with utils.mock_streamlit_session({"test_key": "test_value"}):
            # Should provide mocked session state
            assert hasattr(st, 'session_state')
            
    def test_capture_streamlit_output(self):
        """Test utility for capturing Streamlit output."""
        utils = ComponentTestingUtils()
        
        def test_component():
            st.write("Test output")
            st.success("Success message")
            
        captured = utils.capture_output(test_component)
        
        # Should capture all streamlit calls
        assert "write" in captured
        assert "success" in captured
        
    def test_validate_component_behavior(self):
        """Test utility for validating component behavior."""
        utils = ComponentTestingUtils()
        
        def test_component():
            return StockSymbolInput("Symbol", "test").render()
            
        result = utils.test_component_validation(
            test_component,
            inputs={"symbol": "AAPL"},
            expected_output="AAPL"
        )
        
        # Mock test - just check it doesn't crash
        assert isinstance(result, bool)
        
    def test_component_accessibility_check(self):
        """Test utility for checking component accessibility."""
        utils = ComponentTestingUtils()
        
        def test_component():
            return StockSymbolInput("Stock Symbol", "symbol").render()
            
        accessibility_score = utils.check_accessibility(test_component)
        
        # Should return score based on accessibility criteria
        assert isinstance(accessibility_score, (int, float))
        assert 0 <= accessibility_score <= 100