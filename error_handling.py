"""
Error handling and user feedback system for StockBook.

This module provides comprehensive error handling including:
- Custom exception classes with structured error information
- Error logging system with context preservation
- User-friendly error message mapping
- Streamlit error boundaries
- Success/info message system
- Error recovery suggestions

Design principles:
- Structured error information for debugging
- User-friendly messages that hide technical details
- Contextual error recovery suggestions
- Comprehensive logging for troubleshooting
"""

import logging
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import streamlit as st

from config import config


class StockBookError(Exception):
    """
    Base exception class for all StockBook application errors.

    Provides structured error information including error codes,
    context data, and user-friendly message mapping capabilities.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize StockBook error.

        Args:
            message: Technical error message for developers
            error_code: Standardized error code for categorization
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}

    def __str__(self) -> str:
        """Return string representation of the error."""
        return self.message


class ValidationError(StockBookError):
    """
    Exception raised when data validation fails.

    Includes field-specific information to help users understand
    what input was invalid and why.
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs,
    ):
        """
        Initialize validation error.

        Args:
            message: Error message describing the validation failure
            field: Name of the field that failed validation
            value: The invalid value that caused the error
            **kwargs: Additional context passed to parent class
        """
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field
        self.value = value

        # Add field and value to context for logging/debugging
        if field:
            self.context["field"] = field
            self.context[field] = value
        if value is not None:
            self.context["value"] = value


class DatabaseError(StockBookError):
    """
    Exception raised when database operations fail.

    Includes operation context and query information for debugging
    while providing user-friendly messages about data issues.
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        query: Optional[str] = None,
        params: Optional[tuple] = None,
        **kwargs,
    ):
        """
        Initialize database error.

        Args:
            message: Error message describing the database failure
            operation: Database operation type (SELECT, INSERT, UPDATE, DELETE)
            query: SQL query that failed (for debugging)
            params: Query parameters (for debugging)
            **kwargs: Additional context passed to parent class
        """
        super().__init__(message, error_code="DATABASE_ERROR", **kwargs)
        self.operation = operation
        self.query = query
        self.params = params

        # Add database context for debugging
        if operation:
            self.context["operation"] = operation
        if query:
            self.context["query"] = query
        if params:
            self.context["params"] = params


class BusinessLogicError(StockBookError):
    """
    Exception raised when business rules are violated.

    Includes rule context and current/limit values to help users
    understand why their action was rejected.
    """

    def __init__(
        self,
        message: str,
        rule: Optional[str] = None,
        current_value: Optional[Union[int, float]] = None,
        limit_value: Optional[Union[int, float]] = None,
        **kwargs,
    ):
        """
        Initialize business logic error.

        Args:
            message: Error message describing the rule violation
            rule: Name/identifier of the business rule that was violated
            current_value: Current value that violates the rule
            limit_value: Maximum/minimum allowed value
            **kwargs: Additional context passed to parent class
        """
        super().__init__(message, error_code="BUSINESS_LOGIC_ERROR", **kwargs)
        self.rule = rule
        self.current_value = current_value
        self.limit_value = limit_value

        # Add business rule context
        if rule:
            self.context["rule"] = rule
        if current_value is not None:
            self.context["current_value"] = current_value
        if limit_value is not None:
            self.context["limit_value"] = limit_value


class ErrorLogger:
    """
    Centralized error logging system with structured logging.

    Logs errors with context information, timestamps, and user session data
    for comprehensive debugging and monitoring.
    """

    def __init__(self, log_file: Optional[Path] = None):
        """
        Initialize error logger.

        Args:
            log_file: Path to log file (uses config default if None)
        """
        self.log_file = log_file or config.logs_dir / "errors.log"

        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Configure logger
        self.logger = logging.getLogger("stockbook.errors")
        self.logger.setLevel(logging.ERROR)

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Add file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.ERROR)

        # Create detailed formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def log_error(
        self, error: Exception, user_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error with full context information.

        Args:
            error: Exception instance to log
            user_context: Additional user/session context
        """
        # Build log message with error details
        log_parts = [f"Error: {str(error)}"]

        # Add error type
        log_parts.append(f"Type: {type(error).__name__}")

        # Add StockBook-specific error information
        if isinstance(error, StockBookError):
            if error.error_code:
                log_parts.append(f"Code: {error.error_code}")

            # Add context information
            for key, value in error.context.items():
                log_parts.append(f"{key}: {value}")

        # Add user context if provided
        if user_context:
            for key, value in user_context.items():
                log_parts.append(f"{key}: {value}")

        # Log the complete error information
        log_message = " | ".join(log_parts)
        self.logger.error(log_message, exc_info=True)


class ErrorMessageMapper:
    """
    Maps technical error messages to user-friendly messages.

    Provides context-aware message translation that hides technical
    details while giving users actionable information.
    """

    def __init__(self, custom_mappings: Optional[Dict[str, str]] = None):
        """
        Initialize error message mapper.

        Args:
            custom_mappings: Additional custom error code mappings
        """
        # Default error message mappings
        self.message_mappings = {
            "VALIDATION_ERROR": self._get_validation_message,
            "DATABASE_ERROR": self._get_database_message,
            "BUSINESS_LOGIC_ERROR": self._get_business_logic_message,
        }

        # Add custom mappings if provided
        if custom_mappings:
            self.message_mappings.update(custom_mappings)

    def get_user_message(self, error: Exception) -> str:
        """
        Get user-friendly message for an error.

        Args:
            error: Exception instance to map

        Returns:
            User-friendly error message
        """
        if isinstance(error, StockBookError) and error.error_code:
            mapper = self.message_mappings.get(error.error_code)
            if callable(mapper):
                return mapper(error)
            elif isinstance(mapper, str):
                return mapper

        # Default message for unknown errors
        return "An unexpected error occurred. Please try again or contact support."

    def _get_validation_message(self, error: ValidationError) -> str:
        """Generate user-friendly validation error message."""
        field = getattr(error, "field", None)
        value = getattr(error, "value", None)

        if field == "symbol":
            if value and not str(value).isupper():
                return "Stock symbol must be in uppercase letters (e.g., 'AAPL')"
            elif value and len(str(value)) > config.stock_symbol_max_length:
                return f"Stock symbol must be {config.stock_symbol_max_length} characters or less"
            else:
                return "Please enter a valid stock symbol (1-5 uppercase letters)"

        elif field == "price":
            return "Please enter a valid price (must be greater than $0.01)"

        elif field == "quantity":
            return "Please enter a valid quantity (must be 1 or more shares)"

        elif field == "grade":
            valid_grades = ", ".join(config.valid_grades)
            return f"Stock grade must be one of: {valid_grades}"

        elif field == "name":
            return "Name cannot be empty"

        else:
            return f"Invalid {field or 'input'}. Please check your entry and try again."

    def _get_database_message(self, error: DatabaseError) -> str:
        """Generate user-friendly database error message."""
        message = error.message.lower()

        if "unique" in message or "duplicate" in message:
            return "This item already exists. Please check if it's already been added."

        elif "foreign key" in message or "constraint" in message:
            return "This action cannot be completed due to existing related data."

        elif "connection" in message or "timeout" in message:
            return "Database connection issue. Please try again in a moment."

        elif "not found" in message:
            return "The requested item could not be found."

        else:
            return "A data error occurred. Please try again or contact support."

    def _get_business_logic_message(self, error: BusinessLogicError) -> str:
        """Generate user-friendly business logic error message."""
        rule = getattr(error, "rule", "")
        current_value = getattr(error, "current_value", None)
        limit_value = getattr(error, "limit_value", None)

        if "risk" in rule.lower():
            if current_value and limit_value:
                return (
                    f"Risk limit exceeded: {current_value}% is above the "
                    f"{limit_value}% limit. Please reduce the trade size."
                )
            else:
                return "This trade would exceed your risk limits. Please reduce the trade size."

        elif "position" in rule.lower():
            return (
                "You have reached the maximum number of positions for this portfolio."
            )

        elif "balance" in rule.lower() or "funds" in rule.lower():
            return "Insufficient funds for this transaction."

        else:
            return "This action violates a portfolio rule. Please check your settings."


class StreamlitErrorBoundary:
    """
    Error boundary for Streamlit components.

    Catches exceptions in Streamlit code and displays user-friendly
    error messages while logging technical details.
    """

    def __init__(self, suppress_errors: bool = False):
        """
        Initialize Streamlit error boundary.

        Args:
            suppress_errors: Whether to suppress errors (useful for testing)
        """
        self.suppress_errors = suppress_errors
        self.error_logger = ErrorLogger()
        self.message_mapper = ErrorMessageMapper()

    def handle_error(
        self,
        error: Exception,
        level: str = "error",
        user_context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle an error by logging and displaying user message.

        Args:
            error: Exception to handle
            level: Display level ('error', 'warning', 'info')
            user_context: Additional context for logging
        """
        # Log the error with full technical details
        self.error_logger.log_error(error, user_context)

        # Don't display anything if suppressing errors (testing mode)
        if self.suppress_errors:
            return

        # Get user-friendly message
        user_message = self.message_mapper.get_user_message(error)

        # Display appropriate Streamlit message
        if level == "error":
            st.error(user_message)
        elif level == "warning":
            st.warning(user_message)
        elif level == "info":
            st.info(user_message)

    @contextmanager
    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit - handle any exceptions."""
        if exc_type and issubclass(exc_type, Exception):
            self.handle_error(exc_value)
            return True  # Suppress the exception
        return False


class MessageSystem:
    """
    Success and info message system for user feedback.

    Provides consistent styling and functionality for positive
    user feedback messages.
    """

    def __init__(self):
        """Initialize message system."""
        self.message_queue: List[Dict[str, str]] = []

    def success(self, message: str, auto_dismiss: Optional[float] = None) -> None:
        """
        Display a success message.

        Args:
            message: Success message to display
            auto_dismiss: Seconds after which to auto-dismiss (optional)
        """
        st.success(message)

        if auto_dismiss:
            # Create auto-dismissing message
            container = st.empty()
            container.success(message)
            time.sleep(auto_dismiss)
            container.empty()

    def info(self, message: str, auto_dismiss: Optional[float] = None) -> None:
        """
        Display an info message.

        Args:
            message: Info message to display
            auto_dismiss: Seconds after which to auto-dismiss (optional)
        """
        st.info(message)

        if auto_dismiss:
            container = st.empty()
            container.info(message)
            time.sleep(auto_dismiss)
            container.empty()

    def warning(self, message: str, auto_dismiss: Optional[float] = None) -> None:
        """
        Display a warning message.

        Args:
            message: Warning message to display
            auto_dismiss: Seconds after which to auto-dismiss (optional)
        """
        st.warning(message)

        if auto_dismiss:
            container = st.empty()
            container.warning(message)
            time.sleep(auto_dismiss)
            container.empty()

    def queue_success(self, message: str) -> None:
        """Queue a success message for batch display."""
        self.message_queue.append({"type": "success", "message": message})

    def queue_info(self, message: str) -> None:
        """Queue an info message for batch display."""
        self.message_queue.append({"type": "info", "message": message})

    def queue_warning(self, message: str) -> None:
        """Queue a warning message for batch display."""
        self.message_queue.append({"type": "warning", "message": message})

    def display_queued_messages(self) -> None:
        """Display all queued messages and clear the queue."""
        for msg_data in self.message_queue:
            msg_type = msg_data["type"]
            message = msg_data["message"]

            if msg_type == "success":
                st.success(message)
            elif msg_type == "info":
                st.info(message)
            elif msg_type == "warning":
                st.warning(message)

        # Clear the queue
        self.message_queue.clear()


class ErrorRecovery:
    """
    Provides contextual error recovery suggestions.

    Analyzes errors and provides specific, actionable suggestions
    to help users resolve issues.
    """

    def get_suggestions(self, error: Exception) -> List[str]:
        """
        Get recovery suggestions for an error.

        Args:
            error: Exception to provide suggestions for

        Returns:
            List of actionable recovery suggestions
        """
        if isinstance(error, ValidationError):
            return self._get_validation_suggestions(error)
        elif isinstance(error, DatabaseError):
            return self._get_database_suggestions(error)
        elif isinstance(error, BusinessLogicError):
            return self._get_business_logic_suggestions(error)
        else:
            return self._get_generic_suggestions(error)

    def _get_validation_suggestions(self, error: ValidationError) -> List[str]:
        """Get suggestions for validation errors."""
        field = getattr(error, "field", None)
        suggestions = []

        if field == "symbol":
            suggestions.extend(
                [
                    "Use uppercase letters only (e.g., 'AAPL' not 'aapl')",
                    "Keep symbols between 1-5 characters",
                    "Check if the symbol exists on major exchanges",
                    "Use the company's official ticker symbol",
                ]
            )

        elif field == "price":
            suggestions.extend(
                [
                    "Enter a price greater than $0.01",
                    "Use up to 2 decimal places (e.g., 123.45)",
                    "Don't include currency symbols or commas",
                    "Check current market price if unsure",
                ]
            )

        elif field == "quantity":
            suggestions.extend(
                [
                    "Enter a whole number of shares (e.g., 100)",
                    "Quantity must be at least 1",
                    "Don't use decimal places for share quantities",
                    "Consider your available funds when choosing quantity",
                ]
            )

        elif field == "grade":
            suggestions.extend(
                [
                    f"Choose from available grades: {', '.join(config.valid_grades)}",
                    "Grade represents your assessment of the stock quality",
                    "A = High quality, B = Medium quality, C = Speculative",
                ]
            )

        else:
            suggestions.extend(
                [
                    "Check that all required fields are filled",
                    "Ensure data format matches expected format",
                    "Try clearing the field and entering again",
                ]
            )

        return suggestions

    def _get_database_suggestions(self, error: DatabaseError) -> List[str]:
        """Get suggestions for database errors."""
        message = error.message.lower()
        suggestions = []

        if "unique" in message or "duplicate" in message:
            suggestions.extend(
                [
                    "Check if this item already exists before adding",
                    "Use the search function to find existing items",
                    "Consider updating the existing item instead",
                    "Try a different name or symbol",
                ]
            )

        elif "connection" in message or "timeout" in message:
            suggestions.extend(
                [
                    "Try the operation again in a few moments",
                    "Check your internet connection",
                    "Refresh the page and try again",
                    "Contact support if the problem persists",
                ]
            )

        else:
            suggestions.extend(
                [
                    "Try the operation again",
                    "Refresh the page",
                    "Check that all related data exists",
                ]
            )

        return suggestions

    def _get_business_logic_suggestions(self, error: BusinessLogicError) -> List[str]:
        """Get suggestions for business logic errors."""
        rule = getattr(error, "rule", "").lower()
        current_value = getattr(error, "current_value", None)
        limit_value = getattr(error, "limit_value", None)
        suggestions = []

        if "risk" in rule:
            suggestions.extend(
                [
                    "Reduce the quantity of shares to buy",
                    "Choose a stock with a lower price",
                    "Increase your portfolio's risk limit in settings",
                    "Consider the impact on your overall portfolio risk",
                ]
            )

            if current_value and limit_value:
                suggested_quantity = int((limit_value / current_value) * 100)
                suggestions.append(
                    f"Try reducing to approximately {suggested_quantity}% of current quantity"
                )

        elif "position" in rule:
            suggestions.extend(
                [
                    "Close an existing position before opening a new one",
                    "Increase the maximum positions limit in portfolio settings",
                    "Consider consolidating similar positions",
                    "Review your current holdings for underperforming stocks",
                ]
            )

        elif "balance" in rule or "funds" in rule:
            suggestions.extend(
                [
                    "Add funds to your portfolio",
                    "Reduce the quantity of shares",
                    "Sell some existing positions to free up capital",
                    "Check your available cash balance",
                ]
            )

        else:
            suggestions.extend(
                [
                    "Review your portfolio settings and limits",
                    "Check if your action conflicts with existing rules",
                    "Consider adjusting your portfolio configuration",
                ]
            )

        return suggestions

    def _get_generic_suggestions(self, error: Exception) -> List[str]:
        """Get generic suggestions for unknown errors."""
        return [
            "Try the operation again",
            "Refresh the page and retry",
            "Check your input data for any unusual characters",
            "Contact support if the problem continues",
        ]
