"""
Streamlit implementation of UI operations interfaces.

Provides concrete implementation of UI operations specifically for Streamlit,
isolating all Streamlit-specific code in one place.

TODO: TECH DEBT - Strategic Type Ignores for UI Framework Migration
=================================================================
This file contains broad `# type: ignore` statements added strategically during
type safety improvements to avoid wasting time on temporary Streamlit code.

CLEANUP REQUIRED when migrating to new UI framework:
1. Remove all `# type: ignore[import-untyped]` and `# type: ignore[misc]` statements
2. Replace entire file with new UI framework equivalent operations
3. Maintain same IUIOperations interface for smooth controller integration
"""

import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

# TODO: TECH DEBT - Remove these broad type ignores when replacing Streamlit
import pandas as pd  # type: ignore[import-untyped]
import streamlit as st  # type: ignore[import-untyped]

from src.presentation.interfaces.ui_operations import (  # type: ignore[misc]
    IUILayoutOperations,
    IUIOperations,
    IUIValidationOperations,
)

logger = logging.getLogger(__name__)  # type: ignore[misc]


class StreamlitUIOperations(IUIOperations):
    """Streamlit implementation of basic UI operations."""

    def show_success(self, message: str) -> None:
        """Display a success message to the user."""
        st.success(message)

    def show_error(self, message: str) -> None:
        """Display an error message to the user."""
        st.error(message)

    def show_warning(self, message: str) -> None:
        """Display a warning message to the user."""
        st.warning(message)

    def show_info(self, message: str) -> None:
        """Display an informational message to the user."""
        st.info(message)

    def render_data_table(
        self,
        data: List[Dict[str, Any]],
        columns: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Render a data table with the provided data."""
        if not data:
            self.show_info("No data to display")  # type: ignore[misc]
            return

        df = pd.DataFrame(data)  # type: ignore[misc] - Temporary UI framework
        if columns:
            df = df[columns]  # type: ignore[misc]

        # Apply Streamlit-specific configuration
        streamlit_config = {
            "use_container_width": kwargs.get("use_container_width", True),
            "hide_index": kwargs.get("hide_index", True),
        }

        # Add column configuration if provided
        if "column_config" in kwargs:
            streamlit_config["column_config"] = kwargs["column_config"]

        st.dataframe(df, **streamlit_config)  # type: ignore[misc]

    def render_metric(
        self, label: str, value: str, delta: Optional[str] = None
    ) -> None:
        """Render a metric display."""
        st.metric(label, value, delta)

    def create_columns(self, count: int) -> List[Any]:
        """Create column layout containers."""
        return st.columns(count)  # type: ignore[misc]

    def create_tabs(self, tab_names: List[str]) -> List[Any]:
        """Create tab containers."""
        return st.tabs(tab_names)  # type: ignore[misc] - Temporary UI framework

    def render_header(self, text: str, level: int = 1) -> None:
        """Render a header with the specified level."""
        if level == 1:
            st.header(text)
        elif level == 2:
            st.subheader(text)
        else:
            st.write(f"{'#' * level} {text}")  # type: ignore[misc]

    def render_subheader(self, text: str) -> None:
        """Render a subheader."""
        st.subheader(text)

    def create_form(self, form_id: str) -> Any:
        """Create a form container."""
        return st.form(form_id)

    def create_text_input(
        self, label: str, value: str = "", placeholder: str = "", help_text: str = ""
    ) -> str:
        """Create a text input field."""
        return st.text_input(
            label,
            value=value,
            placeholder=placeholder if placeholder else None,
            help=help_text if help_text else None,
        )  # type: ignore[misc]

    def create_selectbox(
        self, label: str, options: List[str], index: int = 0, help_text: str = ""
    ) -> str:
        """Create a selectbox widget."""
        return st.selectbox(
            label, options=options, index=index, help=help_text if help_text else None
        )  # type: ignore[misc]

    def create_text_area(
        self, label: str, value: str = "", placeholder: str = ""
    ) -> str:
        """Create a text area widget."""
        return st.text_area(
            label, value=value, placeholder=placeholder if placeholder else None
        )  # type: ignore[misc]

    def create_button(self, label: str, button_type: str = "secondary") -> bool:
        """Create a button and return whether it was clicked."""
        return st.button(label, type=button_type)  # type: ignore[misc]

    def create_form_submit_button(self, label: str) -> bool:
        """Create a form submit button."""
        return st.form_submit_button(label, type="primary")

    def trigger_celebration(self) -> None:
        """Trigger a celebration animation (like balloons)."""
        st.balloons()

    def trigger_rerun(self) -> None:
        """Trigger a page refresh/rerun."""
        st.rerun()


class StreamlitUILayoutOperations(IUILayoutOperations):
    """Streamlit implementation of layout operations."""

    def create_sidebar(self) -> Any:
        """Create a sidebar container."""
        return st.sidebar

    def create_expander(self, label: str, expanded: bool = False) -> Any:
        """Create an expandable container."""
        return st.expander(label, expanded=expanded)

    @contextmanager
    def within_container(self, container: Any):
        """Create a context manager for working within a container."""
        with container:
            yield container


class StreamlitUIValidationOperations(IUIValidationOperations):
    """Streamlit implementation of validation operations."""

    def display_validation_errors(self, errors: Dict[str, str]) -> None:
        """Display validation errors to the user."""
        if not errors:
            return

        error_message = self.format_error_message(errors)  # type: ignore[misc]
        st.error(error_message)

    def display_field_errors(self, field_errors: List[str]) -> None:
        """Display a list of field-specific errors."""
        if not field_errors:
            return

        error_message = (
            "⚠️ Please fix the following errors:\n\n"
            + "\n".join(f"• {error}" for error in field_errors)
            + "\n"
        )

        st.error(error_message)

    def format_error_message(self, errors: Dict[str, str]) -> str:
        """Format validation errors into a user-friendly message."""
        if not errors:
            return ""

        if len(errors) == 1:
            field, message = next(iter(errors.items()))  # type: ignore[misc]
            return f"⚠️ {field}: {message}"

        error_message = f"⚠️ Please fix the following {len(errors)} errors:\n\n"
        for field, message in errors.items():
            error_message += f"• {field}: {message}\n"

        return error_message


class StreamlitUIOperationsFacade:
    """
    Facade that combines all Streamlit UI operations.

    Provides a single interface for all UI operations while maintaining
    the separation of concerns between different operation types.
    """

    def __init__(self):
        """Initialize Streamlit UI operations facade with all operation components.

        Creates instances of UI operations, layout operations, and validation operations
        to provide a unified interface for Streamlit-based user interface interactions.
        """
        self.ui = StreamlitUIOperations()  # type: ignore[misc]
        self.layout = StreamlitUILayoutOperations()  # type: ignore[misc]
        self.validation = StreamlitUIValidationOperations()  # type: ignore[misc]

    # type: ignore[misc]

    @property
    def operations(self) -> StreamlitUIOperations:
        """Get basic UI operations."""
        return self.ui

    @property
    def layout_operations(self) -> StreamlitUILayoutOperations:
        """Get layout operations."""
        return self.layout

    @property
    def validation_operations(self) -> StreamlitUIValidationOperations:
        """Get validation operations."""
        return self.validation
