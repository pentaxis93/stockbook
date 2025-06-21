"""
UI operations interface for presentation layer.

Provides abstractions for common UI operations to reduce coupling
between presentation logic and specific UI frameworks.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IUIOperations(ABC):
    """
    Interface for UI operations to support multiple UI frameworks.

    This abstraction allows the presentation layer to be framework-agnostic
    while still providing rich UI functionality.
    """

    @abstractmethod
    def show_success(self, message: str) -> None:
        """Display a success message to the user."""
        pass

    @abstractmethod
    def show_error(self, message: str) -> None:
        """Display an error message to the user."""
        pass

    @abstractmethod
    def show_warning(self, message: str) -> None:
        """Display a warning message to the user."""
        pass

    @abstractmethod
    def show_info(self, message: str) -> None:
        """Display an informational message to the user."""
        pass

    @abstractmethod
    def render_data_table(
        self,
        data: List[Dict[str, Any]],
        columns: Optional[List[str]] = None,
        **kwargs: Any
    ) -> None:
        """Render a data table with the provided data."""
        pass

    @abstractmethod
    def render_metric(
        self, label: str, value: str, delta: Optional[str] = None
    ) -> None:
        """Render a metric display."""
        pass

    @abstractmethod
    def create_columns(self, count: int) -> List[Any]:
        """Create column layout containers."""
        pass

    @abstractmethod
    def create_tabs(self, tab_names: List[str]) -> List[Any]:
        """Create tab containers."""
        pass

    @abstractmethod
    def render_header(self, text: str, level: int = 1) -> None:
        """Render a header with the specified level."""
        pass

    @abstractmethod
    def render_subheader(self, text: str) -> None:
        """Render a subheader."""
        pass

    @abstractmethod
    def create_form(self, form_id: str) -> Any:
        """Create a form container."""
        pass

    @abstractmethod
    def create_text_input(
        self, label: str, value: str = "", placeholder: str = "", help_text: str = ""
    ) -> str:
        """Create a text input field."""
        pass

    @abstractmethod
    def create_selectbox(
        self, label: str, options: List[str], index: int = 0, help_text: str = ""
    ) -> str:
        """Create a selectbox widget."""
        pass

    @abstractmethod
    def create_text_area(
        self, label: str, value: str = "", placeholder: str = ""
    ) -> str:
        """Create a text area widget."""
        pass

    @abstractmethod
    def create_button(self, label: str, button_type: str = "secondary") -> bool:
        """Create a button and return whether it was clicked."""
        pass

    @abstractmethod
    def create_form_submit_button(self, label: str) -> bool:
        """Create a form submit button."""
        pass

    @abstractmethod
    def trigger_celebration(self) -> None:
        """Trigger a celebration animation (like balloons)."""
        pass

    @abstractmethod
    def trigger_rerun(self) -> None:
        """Trigger a page refresh/rerun."""
        pass


class IUILayoutOperations(ABC):
    """
    Interface for UI layout operations.

    Provides abstraction for layout-specific operations that may vary
    between different UI frameworks.
    """

    @abstractmethod
    def create_sidebar(self) -> Any:
        """Create a sidebar container."""
        pass

    @abstractmethod
    def create_expander(self, label: str, expanded: bool = False) -> Any:
        """Create an expandable container."""
        pass

    @abstractmethod
    def within_container(self, container: Any) -> Any:
        """Create a context manager for working within a container."""
        pass


class IUIValidationOperations(ABC):
    """
    Interface for UI validation and feedback operations.

    Handles validation error display and user feedback in a
    framework-agnostic way.
    """

    @abstractmethod
    def display_validation_errors(self, errors: Dict[str, str]) -> None:
        """Display validation errors to the user."""
        pass

    @abstractmethod
    def display_field_errors(self, field_errors: List[str]) -> None:
        """Display a list of field-specific errors."""
        pass

    @abstractmethod
    def format_error_message(self, errors: Dict[str, str]) -> str:
        """Format validation errors into a user-friendly message."""
        pass
