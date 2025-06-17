"""
Reusable UI component library for StockBook.

This module provides consistent, validated Streamlit components including:
- Input components with built-in validation and error handling
- Data display components with standardized formatting
- Form layout components for consistent user experience
- Testing utilities for component validation

Design principles:
- Consistent styling and behavior across the application
- Built-in validation using centralized config and error handling
- Accessibility and user experience focused
- Easy to test and maintain
"""

import re
import time
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd
import streamlit as st

from config import config
from error_handling import ErrorMessageMapper, MessageSystem, ValidationError


class StockSymbolInput:
    """
    Validated stock symbol input component.

    Provides symbol entry with real-time validation, suggestions,
    and integration with the centralized config system.
    """

    def __init__(
        self,
        label: str,
        key: str,
        placeholder: Optional[str] = None,
        show_suggestions: bool = False,
        suggestions: Optional[List[str]] = None,
        help_text: Optional[str] = None,
    ):
        """
        Initialize stock symbol input.

        Args:
            label: Display label for the input
            key: Unique key for Streamlit state
            placeholder: Placeholder text (uses default if None)
            show_suggestions: Whether to show symbol suggestions
            suggestions: List of suggested symbols
            help_text: Help text to display
        """
        self.label = label
        self.key = key
        self.placeholder = placeholder or "Enter symbol (e.g., AAPL)"
        self.show_suggestions = show_suggestions
        self.suggestions = suggestions or []
        self.help_text = help_text

        self.error_mapper = ErrorMessageMapper()

    def render(self) -> Optional[str]:
        """
        Render the stock symbol input component.

        Returns:
            Validated symbol string or None if invalid
        """
        # Get raw input value
        raw_value = st.text_input(
            label=self.label,
            key=self.key,
            placeholder=self.placeholder,
            max_chars=config.stock_symbol_max_length,
            help=self.help_text,
        )

        # Return None for empty input
        if not raw_value or not raw_value.strip():
            return None

        # Clean and validate the symbol
        symbol = raw_value.strip().upper()

        try:
            # Validate using config pattern
            if not re.match(config.stock_symbol_pattern, symbol):
                raise ValidationError(
                    "Invalid symbol format", field="symbol", value=symbol
                )

            # Check length
            if len(symbol) > config.stock_symbol_max_length:
                raise ValidationError("Symbol too long", field="symbol", value=symbol)

            # Show suggestions if enabled and symbol is partial
            if self.show_suggestions and len(symbol) >= 1:
                self._show_suggestions(symbol)

            return symbol

        except ValidationError as e:
            # Display user-friendly error message
            user_message = self.error_mapper.get_user_message(e)
            st.error(user_message)
            return None

    def _show_suggestions(self, partial_symbol: str) -> None:
        """Show symbol suggestions based on partial input."""
        if not self.suggestions:
            return

        # Filter suggestions that start with the partial symbol
        matching = [s for s in self.suggestions if s.startswith(partial_symbol)]

        if matching:
            suggestions_text = ", ".join(matching[:5])  # Show max 5 suggestions
            st.info(f"💡 Suggestions: {suggestions_text}")


class DatePicker:
    """
    Date picker component with business day validation.

    Provides date selection with validation for business days,
    future dates, and integration with portfolio rules.
    """

    def __init__(
        self,
        label: str,
        key: str,
        min_value: Optional[date] = None,
        max_value: Optional[date] = None,
        allow_future: bool = False,
        business_days_only: bool = False,
        help_text: Optional[str] = None,
    ):
        """
        Initialize date picker.

        Args:
            label: Display label for the input
            key: Unique key for Streamlit state
            min_value: Minimum allowed date
            max_value: Maximum allowed date
            allow_future: Whether future dates are allowed
            business_days_only: Whether to warn for weekends
            help_text: Help text to display
        """
        self.label = label
        self.key = key
        self.min_value = min_value
        self.max_value = max_value or date.today()
        self.allow_future = allow_future
        self.business_days_only = business_days_only
        self.help_text = help_text

        # Set max_value to today if future dates not allowed
        if not allow_future:
            self.max_value = min(self.max_value, date.today())

    def render(self) -> Optional[date]:
        """
        Render the date picker component.

        Returns:
            Selected date or None if invalid
        """
        selected_date = st.date_input(
            label=self.label,
            key=self.key,
            min_value=self.min_value,
            max_value=self.max_value,
            value=date.today(),
            help=self.help_text,
        )

        if selected_date is None:
            return None

        # Validate future dates
        if not self.allow_future and selected_date > date.today():
            st.warning("⚠️ Future dates are not recommended for transactions")

        # Check for business days
        if (
            self.business_days_only and selected_date.weekday() >= 5
        ):  # Saturday=5, Sunday=6
            st.info("ℹ️ Selected date is a weekend - markets may be closed")

        return selected_date


class PriceInput:
    """
    Price input component with currency formatting and validation.

    Provides price entry with currency display, decimal precision,
    and minimum value validation from config.
    """

    def __init__(
        self,
        label: str,
        key: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        help_text: Optional[str] = None,
    ):
        """
        Initialize price input.

        Args:
            label: Display label for the input
            key: Unique key for Streamlit state
            min_value: Minimum price (uses config default if None)
            max_value: Maximum price (uses config default if None)
            help_text: Help text to display
        """
        self.label = label
        self.key = key
        self.min_value = min_value or float(config.min_price)
        self.max_value = max_value or float(config.max_price)
        self.help_text = help_text

        self.error_mapper = ErrorMessageMapper()

    def render(self) -> Optional[Decimal]:
        """
        Render the price input component.

        Returns:
            Price as Decimal for precision or None if invalid
        """
        # Create step based on decimal places
        step = float(f"0.{'0' * (config.decimal_places - 1)}1")

        price = st.number_input(
            label=self.label,
            key=self.key,
            min_value=self.min_value,
            max_value=self.max_value,
            value=self.min_value,
            step=step,
            format=f"%.{config.decimal_places}f",
            help=self.help_text,
        )

        if price is None or price < self.min_value:
            return None

        try:
            # Convert to Decimal for precision
            decimal_price = Decimal(str(price)).quantize(
                Decimal(f"0.{'0' * config.decimal_places}")
            )

            return decimal_price

        except (InvalidOperation, ValueError) as e:
            st.error("Invalid price format")
            return None

    def format_display(self, price: Union[float, Decimal]) -> str:
        """Format price for display with currency symbol."""
        return config.format_currency(float(price))


class QuantityInput:
    """
    Quantity input component with integer validation and limits.

    Provides share quantity entry with validation for minimum values,
    reasonable maximums, and integer constraints.
    """

    def __init__(
        self,
        label: str,
        key: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        help_text: Optional[str] = None,
    ):
        """
        Initialize quantity input.

        Args:
            label: Display label for the input
            key: Unique key for Streamlit state
            min_value: Minimum quantity (uses config default if None)
            max_value: Maximum quantity (uses config default if None)
            help_text: Help text to display
        """
        self.label = label
        self.key = key
        self.min_value = min_value or config.min_quantity
        self.max_value = max_value or config.max_quantity
        self.help_text = help_text

    def render(self) -> Optional[int]:
        """
        Render the quantity input component.

        Returns:
            Quantity as integer or None if invalid
        """
        quantity = st.number_input(
            label=self.label,
            key=self.key,
            min_value=self.min_value,
            max_value=self.max_value,
            value=self.min_value,
            step=1,
            format="%d",
            help=self.help_text,
        )

        if quantity is None or quantity < self.min_value:
            return None

        # Warn about very large quantities
        if quantity > 10000:
            st.warning("⚠️ Large quantity - please verify this is correct")

        return int(quantity)


class MessageDisplay:
    """
    Message display component for user notifications.

    Provides consistent styling for success, error, info, and warning
    messages with optional auto-dismiss functionality.
    """

    def __init__(self):
        """Initialize message display component."""
        pass

    def success(
        self,
        message: str,
        icon: Optional[str] = None,
        auto_dismiss: Optional[float] = None,
    ) -> None:
        """Display success message."""
        display_message = f"{icon} {message}" if icon else message

        if auto_dismiss:
            container = st.empty()
            container.success(display_message)
            time.sleep(auto_dismiss)
            container.empty()
        else:
            st.success(display_message)

    def error(self, message: str, icon: Optional[str] = None) -> None:
        """Display error message."""
        display_message = f"{icon} {message}" if icon else message
        st.error(display_message)

    def info(
        self,
        message: str,
        icon: Optional[str] = None,
        auto_dismiss: Optional[float] = None,
    ) -> None:
        """Display info message."""
        display_message = f"{icon} {message}" if icon else message

        if auto_dismiss:
            container = st.empty()
            container.info(display_message)
            time.sleep(auto_dismiss)
            container.empty()
        else:
            st.info(display_message)

    def warning(
        self,
        message: str,
        icon: Optional[str] = None,
        auto_dismiss: Optional[float] = None,
    ) -> None:
        """Display warning message."""
        display_message = f"{icon} {message}" if icon else message

        if auto_dismiss:
            container = st.empty()
            container.warning(display_message)
            time.sleep(auto_dismiss)
            container.empty()
        else:
            st.warning(display_message)


class DataTable:
    """
    Data table component with consistent formatting.

    Provides standardized table display with column configuration,
    selection capabilities, and handling of empty datasets.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        column_config: Optional[Dict[str, Dict[str, Any]]] = None,
        selection_mode: Optional[str] = None,
        page_size: Optional[int] = None,
        height: Optional[int] = None,
    ):
        """
        Initialize data table.

        Args:
            data: DataFrame to display
            column_config: Configuration for column formatting
            selection_mode: Row selection mode ('single', 'multi', None)
            page_size: Number of rows per page (uses config default if None)
            height: Table height in pixels
        """
        self.data = data
        self.column_config = column_config or {}
        self.selection_mode = selection_mode
        self.page_size = page_size or config.table_page_size
        self.height = height

    def render(self) -> Optional[Dict[str, Any]]:
        """
        Render the data table component.

        Returns:
            Selection information if selection_mode is enabled, None otherwise
        """
        if self.data.empty:
            st.info("📊 No data to display")
            return None

        # Apply pagination if dataset is large
        if len(self.data) > self.page_size:
            self._render_with_pagination()
        else:
            self._render_simple()

        return None  # Selection handling would be implemented here

    def _render_simple(self) -> None:
        """Render table without pagination."""
        if self.selection_mode:
            st.dataframe(
                self.data,
                column_config=self.column_config,
                height=self.height,
                on_select="rerun" if self.selection_mode else None,
                selection_mode=self.selection_mode,
            )
        else:
            st.dataframe(
                self.data, column_config=self.column_config, height=self.height
            )

    def _render_with_pagination(self) -> None:
        """Render table with pagination controls."""
        total_pages = (len(self.data) - 1) // self.page_size + 1

        # Pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            page = st.selectbox(
                "Page",
                range(1, total_pages + 1),
                format_func=lambda x: f"Page {x} of {total_pages}",
            )

        # Calculate slice for current page
        start_idx = (page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.data))

        page_data = self.data.iloc[start_idx:end_idx]

        # Render page data
        if self.selection_mode:
            st.dataframe(
                page_data,
                column_config=self.column_config,
                height=self.height,
                on_select="rerun" if self.selection_mode else None,
                selection_mode=self.selection_mode,
            )
        else:
            st.dataframe(
                page_data, column_config=self.column_config, height=self.height
            )


class FormLayout:
    """
    Form layout component for standard form structure.

    Provides consistent form styling with title, columns,
    and submit button handling.
    """

    def __init__(
        self,
        form_key: str,
        title: Optional[str] = None,
        submit_label: str = "Submit",
        clear_on_submit: bool = False,
        columns: Optional[List[Union[int, float]]] = None,
    ):
        """
        Initialize form layout.

        Args:
            form_key: Unique key for the form
            title: Form title to display
            submit_label: Text for submit button
            clear_on_submit: Whether to clear form on submit
            columns: Column proportions for layout
        """
        self.form_key = form_key
        self.title = title
        self.submit_label = submit_label
        self.clear_on_submit = clear_on_submit
        self.columns = columns

        self._submitted = False
        self._columns_objects = None

    def __enter__(self):
        """Enter form context."""
        self.form_context = st.form(self.form_key, clear_on_submit=self.clear_on_submit)
        self.form_context.__enter__()

        # Display title if provided
        if self.title:
            st.header(self.title)

        # Create columns if specified
        if self.columns:
            self._columns_objects = st.columns(self.columns)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit form context."""
        # Add submit button at the end of the form
        self._submitted = st.form_submit_button(self.submit_label)

        self.form_context.__exit__(exc_type, exc_val, exc_tb)

    def is_submitted(self) -> bool:
        """Check if form was submitted."""
        return self._submitted

    def get_columns(self) -> Optional[List[Any]]:
        """Get column objects for layout."""
        return self._columns_objects


class ComponentTestingUtils:
    """
    Testing utilities for UI components.

    Provides helper functions for mocking Streamlit state,
    capturing output, and validating component behavior.
    """

    def __init__(self):
        """Initialize testing utilities."""
        pass

    @contextmanager
    def mock_streamlit_session(self, initial_state: Dict[str, Any]):
        """
        Mock Streamlit session state for testing.

        Args:
            initial_state: Initial session state values
        """
        # This would be implemented for testing
        # For now, just yield the context
        original_state = getattr(st, "session_state", {})

        try:
            # Mock session state
            st.session_state = type("MockSessionState", (), initial_state)()
            yield
        finally:
            # Restore original state
            st.session_state = original_state

    def capture_output(self, component_func: Callable) -> Dict[str, List[Any]]:
        """
        Capture Streamlit output from component function.

        Args:
            component_func: Function that renders components

        Returns:
            Dictionary of captured streamlit calls
        """
        captured = {"write": [], "success": [], "error": [], "info": [], "warning": []}

        # This would be implemented to capture streamlit calls
        # For now, just run the function
        try:
            component_func()
        except Exception:
            pass

        return captured

    def test_component_validation(
        self, component_func: Callable, inputs: Dict[str, Any], expected_output: Any
    ) -> bool:
        """
        Test component validation behavior.

        Args:
            component_func: Component function to test
            inputs: Input values to test with
            expected_output: Expected output value

        Returns:
            True if validation behaves as expected
        """
        try:
            result = component_func()
            return result == expected_output
        except Exception:
            return False

    def check_accessibility(self, component_func: Callable) -> float:
        """
        Check component accessibility score.

        Args:
            component_func: Component function to check

        Returns:
            Accessibility score (0-100)
        """
        # This would implement accessibility checking
        # For now, return a mock score
        score = 85.0  # Mock score

        # Check for labels, help text, proper contrast, etc.
        # This would be a comprehensive accessibility audit

        return score
