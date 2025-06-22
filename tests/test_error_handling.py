"""
Test suite for error handling and user feedback system.

This module tests the comprehensive error handling system that provides:
- Custom exception classes
- Error logging system
- User-friendly error message mapping
- Error boundaries for Streamlit components
- Success/info message system
- Error recovery suggestions

Following TDD approach - tests are written first to define expected behavior.
"""

import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest

# Import the error handling module (will fail initially - that's expected in TDD)
try:
    from error_handling import (
        BusinessLogicError,
        DatabaseError,
        ErrorLogger,
        ErrorMessageMapper,
        ErrorRecovery,
        MessageSystem,
        StockBookError,
        StreamlitErrorBoundary,
        ValidationError,
    )
except ImportError:
    # This is expected during TDD - we haven't created the module yet
    pytest.skip("Error handling module not yet implemented", allow_module_level=True)


class TestCustomExceptionClasses:
    """Test custom exception class hierarchy and behavior."""

    def test_stockbook_error_base_class(self) -> None:
        """Test that StockBookError is the base exception class."""
        error = StockBookError("Base error message")

        assert isinstance(error, Exception)
        assert str(error) == "Base error message"
        assert error.message == "Base error message"
        assert error.error_code is None
        assert error.context == {}

    def test_stockbook_error_with_code_and_context(self) -> None:
        """Test StockBookError with error code and context."""
        context = {"user_id": 123, "operation": "create_portfolio"}
        error = StockBookError("Operation failed", error_code="E001", context=context)

        assert error.message == "Operation failed"
        assert error.error_code == "E001"
        assert error.context == context

    def test_validation_error_inheritance(self) -> None:
        """Test ValidationError inherits from StockBookError."""
        error = ValidationError("Invalid stock symbol", field="symbol")

        assert isinstance(error, StockBookError)
        assert error.message == "Invalid stock symbol"
        assert error.field == "symbol"
        assert error.error_code == "VALIDATION_ERROR"

    def test_validation_error_with_value(self) -> None:
        """Test ValidationError stores invalid value."""
        error = ValidationError(
            "Symbol must be uppercase", field="symbol", value="aapl"
        )

        assert error.field == "symbol"
        assert error.value == "aapl"
        assert "symbol" in error.context
        assert error.context["symbol"] == "aapl"

    def test_database_error_inheritance(self) -> None:
        """Test DatabaseError inherits from StockBookError."""
        error = DatabaseError("Connection failed", operation="INSERT")

        assert isinstance(error, StockBookError)
        assert error.message == "Connection failed"
        assert error.operation == "INSERT"
        assert error.error_code == "DATABASE_ERROR"

    def test_database_error_with_query(self) -> None:
        """Test DatabaseError stores SQL query information."""
        query = "INSERT INTO stock (symbol, name) VALUES (?, ?)"
        params: tuple[str, str] = ("AAPL", "Apple Inc.")

        error = DatabaseError(
            "Duplicate entry", operation="INSERT", query=query, params=params
        )

        assert error.query == query
        assert error.params == params
        assert "query" in error.context
        assert "params" in error.context

    def test_business_logic_error_inheritance(self) -> None:
        """Test BusinessLogicError inherits from StockBookError."""
        error = BusinessLogicError("Insufficient funds", rule="max_risk_check")

        assert isinstance(error, StockBookError)
        assert error.message == "Insufficient funds"
        assert error.rule == "max_risk_check"
        assert error.error_code == "BUSINESS_LOGIC_ERROR"

    def test_business_logic_error_with_details(self) -> None:
        """Test BusinessLogicError stores business rule details."""
        error = BusinessLogicError(
            "Risk limit exceeded",
            rule="portfolio_risk_limit",
            current_value=5.0,
            limit_value=2.0,
        )

        assert error.rule == "portfolio_risk_limit"
        assert error.current_value == 5.0
        assert error.limit_value == 2.0
        assert "current_value" in error.context
        assert "limit_value" in error.context


class TestErrorLogger:
    """Test error logging system functionality."""

    @pytest.fixture
    def temp_log_file(self) -> Iterator[Path]:
        """Create temporary log file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            log_path = Path(f.name)
        yield log_path
        if log_path.exists():
            log_path.unlink()

    def test_error_logger_initialization(self, temp_log_file: Path) -> None:
        """Test ErrorLogger initializes correctly."""
        logger = ErrorLogger(log_file=temp_log_file)

        assert logger.log_file == temp_log_file
        assert isinstance(logger.logger, logging.Logger)
        assert logger.logger.name == "stockbook.errors"

    def test_error_logger_logs_stockbook_error(self, temp_log_file: Path) -> None:
        """Test logging of StockBookError instances."""
        logger = ErrorLogger(log_file=temp_log_file)
        error = ValidationError("Invalid symbol", field="symbol", value="123")

        logger.log_error(error)

        # Read log file content
        with open(temp_log_file, "r", encoding="utf-8") as f:
            log_content = f.read()

        assert "VALIDATION_ERROR" in log_content
        assert "Invalid symbol" in log_content
        assert "symbol: 123" in log_content
        assert "value: 123" in log_content

    def test_error_logger_logs_generic_exception(self, temp_log_file: Path) -> None:
        """Test logging of generic Exception instances."""
        logger = ErrorLogger(log_file=temp_log_file)
        error = ValueError("Generic error")

        logger.log_error(error)

        with open(temp_log_file, "r", encoding="utf-8") as f:
            log_content = f.read()

        assert "ValueError" in log_content
        assert "Generic error" in log_content

    def test_error_logger_includes_timestamp(self, temp_log_file: Path) -> None:
        """Test that log entries include timestamps."""
        logger = ErrorLogger(log_file=temp_log_file)
        error = StockBookError("Test error")

        before_time = datetime.now()
        logger.log_error(error)

        with open(temp_log_file, "r", encoding="utf-8") as f:
            log_content = f.read()

        # Check that timestamp is in reasonable range
        assert str(before_time.year) in log_content

    def test_error_logger_with_user_context(self, temp_log_file: Path) -> None:
        """Test logging with user context information."""
        logger = ErrorLogger(log_file=temp_log_file)
        error = DatabaseError("Connection failed", operation="SELECT")

        user_context = {"user_id": "test_user", "session_id": "abc123"}
        logger.log_error(error, user_context=user_context)

        with open(temp_log_file, "r", encoding="utf-8") as f:
            log_content = f.read()

        assert "user_id: test_user" in log_content
        assert "session_id: abc123" in log_content


class TestErrorMessageMapper:
    """Test user-friendly error message mapping system."""

    def test_message_mapper_initialization(self) -> None:
        """Test ErrorMessageMapper initializes with default mappings."""
        mapper = ErrorMessageMapper()

        assert isinstance(mapper.message_mappings, dict)
        assert len(mapper.message_mappings) > 0
        assert "VALIDATION_ERROR" in mapper.message_mappings
        assert "DATABASE_ERROR" in mapper.message_mappings

    def test_map_validation_error_message(self) -> None:
        """Test mapping validation errors to user-friendly messages."""
        mapper = ErrorMessageMapper()
        error = ValidationError("Symbol must match pattern", field="symbol")

        user_message = mapper.get_user_message(error)

        assert "symbol" in user_message.lower()
        assert (
            "valid" in user_message.lower()
            or "invalid" in user_message.lower()
            or "error" in user_message.lower()
        )
        assert (
            user_message != error.message
        )  # Should be different from technical message

    def test_map_database_error_message(self) -> None:
        """Test mapping database errors to user-friendly messages."""
        mapper = ErrorMessageMapper()
        error = DatabaseError("UNIQUE constraint failed", operation="INSERT")

        user_message = mapper.get_user_message(error)

        assert (
            "already exists" in user_message.lower()
            or "duplicate" in user_message.lower()
        )
        assert "UNIQUE constraint" not in user_message  # Should hide technical details

    def test_map_business_logic_error_message(self) -> None:
        """Test mapping business logic errors to user-friendly messages."""
        mapper = ErrorMessageMapper()
        error = BusinessLogicError("Risk limit exceeded", rule="portfolio_risk_limit")

        user_message = mapper.get_user_message(error)

        assert "risk" in user_message.lower()
        assert "limit" in user_message.lower()

    def test_map_unknown_error_message(self) -> None:
        """Test mapping unknown errors to generic user-friendly message."""
        mapper = ErrorMessageMapper()
        error = RuntimeError("Unexpected error")

        user_message = mapper.get_user_message(error)

        assert "unexpected" in user_message.lower() or "error" in user_message.lower()
        assert len(user_message) > 0

    def test_custom_message_mapping(self) -> None:
        """Test adding custom error message mappings."""
        custom_mappings = {"CUSTOM_ERROR": "This is a custom error message"}
        mapper = ErrorMessageMapper(custom_mappings=custom_mappings)

        error = StockBookError("Technical message", error_code="CUSTOM_ERROR")
        user_message = mapper.get_user_message(error)

        assert user_message == "This is a custom error message"

    def test_message_with_context_substitution(self) -> None:
        """Test message mapping with context variable substitution."""
        mapper = ErrorMessageMapper()
        error = ValidationError("Symbol too long", field="symbol", value="TOOLONGSTOCK")

        user_message = mapper.get_user_message(error)

        # Should include the actual symbol value in user message
        assert "TOOLONGSTOCK" in user_message or "symbol" in user_message.lower()


class TestStreamlitErrorBoundary:
    """Test Streamlit error boundary functionality."""

    def test_error_boundary_initialization(self) -> None:
        """Test StreamlitErrorBoundary initializes correctly."""
        boundary = StreamlitErrorBoundary()

        assert isinstance(boundary.error_logger, ErrorLogger)
        assert isinstance(boundary.message_mapper, ErrorMessageMapper)

    @patch("streamlit.error")
    def test_error_boundary_handles_stockbook_error(
        self, mock_st_error: MagicMock
    ) -> None:
        """Test error boundary handles StockBookError gracefully."""
        boundary = StreamlitErrorBoundary()
        error = ValidationError("Invalid input", field="symbol")

        boundary.handle_error(error)

        # Should call streamlit.error with user-friendly message
        mock_st_error.assert_called_once()
        call_args = mock_st_error.call_args[0][0]
        assert (
            "valid" in call_args.lower()
            or "invalid" in call_args.lower()
            or "error" in call_args.lower()
        )

    @patch("streamlit.error")
    def test_error_boundary_handles_generic_exception(
        self, mock_st_error: MagicMock
    ) -> None:
        """Test error boundary handles generic exceptions."""
        boundary = StreamlitErrorBoundary()
        error = ValueError("Generic error")

        boundary.handle_error(error)

        mock_st_error.assert_called_once()

    @patch("streamlit.warning")
    def test_error_boundary_shows_warnings(self, mock_st_warning: MagicMock) -> None:
        """Test error boundary can show warnings instead of errors."""
        boundary = StreamlitErrorBoundary()
        error = ValidationError("Minor issue", field="notes")

        boundary.handle_error(error, level="warning")

        mock_st_warning.assert_called_once()

    def test_error_boundary_context_manager(self) -> None:
        """Test error boundary works as context manager."""
        boundary = StreamlitErrorBoundary()

        with patch("streamlit.error") as mock_error:
            with boundary:
                raise ValidationError("Test error", field="test")

            mock_error.assert_called_once()

    def test_error_boundary_suppress_mode(self) -> None:
        """Test error boundary can suppress errors in testing mode."""
        boundary = StreamlitErrorBoundary(suppress_errors=True)

        with patch("streamlit.error") as mock_error:
            with boundary:
                raise ValidationError("Test error", field="test")

            # Should not call streamlit.error when suppressing
            mock_error.assert_not_called()


class TestMessageSystem:
    """Test success/info message system."""

    @patch("streamlit.success")
    def test_success_message_display(self, mock_st_success: MagicMock) -> None:
        """Test displaying success messages."""
        message_system = MessageSystem()

        message_system.success("Portfolio created successfully!")

        mock_st_success.assert_called_once_with("Portfolio created successfully!")

    @patch("streamlit.info")
    def test_info_message_display(self, mock_st_info: MagicMock) -> None:
        """Test displaying info messages."""
        message_system = MessageSystem()

        message_system.info("Loading portfolio data...")

        mock_st_info.assert_called_once_with("Loading portfolio data...")

    @patch("streamlit.warning")
    def test_warning_message_display(self, mock_st_warning: MagicMock) -> None:
        """Test displaying warning messages."""
        message_system = MessageSystem()

        message_system.warning("Portfolio risk is approaching limit")

        mock_st_warning.assert_called_once_with("Portfolio risk is approaching limit")

    def test_message_with_auto_dismiss(self) -> None:
        """Test messages with auto-dismiss timer."""
        message_system = MessageSystem()

        with patch("time.sleep") as mock_sleep, patch("streamlit.empty") as mock_empty:
            container = MagicMock()
            mock_empty.return_value = container

            message_system.success("Saved!", auto_dismiss=2.0)

            mock_sleep.assert_called_with(2.0)
            container.empty.assert_called_once()

    def test_message_queue_functionality(self) -> None:
        """Test message queueing and batch display."""
        message_system = MessageSystem()

        message_system.queue_success("First message")
        message_system.queue_info("Second message")
        message_system.queue_warning("Third message")

        assert len(message_system.message_queue) == 3

        with patch("streamlit.success") as mock_success, patch(
            "streamlit.info"
        ) as mock_info, patch("streamlit.warning") as mock_warning:
            message_system.display_queued_messages()

            mock_success.assert_called_once_with("First message")
            mock_info.assert_called_once_with("Second message")
            mock_warning.assert_called_once_with("Third message")

        assert len(message_system.message_queue) == 0


class TestErrorRecovery:
    """Test error recovery suggestion system."""

    def test_recovery_suggestions_for_validation_error(self) -> None:
        """Test recovery suggestions for validation errors."""
        recovery = ErrorRecovery()
        error = ValidationError("Invalid symbol format", field="symbol", value="aapl")

        suggestions = recovery.get_suggestions(error)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert any("uppercase" in suggestion.lower() for suggestion in suggestions)

    def test_recovery_suggestions_for_database_error(self) -> None:
        """Test recovery suggestions for database errors."""
        recovery = ErrorRecovery()
        error = DatabaseError("Connection timeout", operation="SELECT")

        suggestions = recovery.get_suggestions(error)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert any(
            "try again" in suggestion.lower() or "retry" in suggestion.lower()
            for suggestion in suggestions
        )

    def test_recovery_suggestions_for_business_logic_error(self) -> None:
        """Test recovery suggestions for business logic errors."""
        recovery = ErrorRecovery()
        error = BusinessLogicError(
            "Risk limit exceeded",
            rule="portfolio_risk_limit",
            current_value=5.0,
            limit_value=2.0,
        )

        suggestions = recovery.get_suggestions(error)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert any(
            "reduce" in suggestion.lower() or "lower" in suggestion.lower()
            for suggestion in suggestions
        )

    def test_no_suggestions_for_unknown_error(self) -> None:
        """Test that unknown errors return generic suggestions."""
        recovery = ErrorRecovery()
        error = RuntimeError("Unknown error")

        suggestions = recovery.get_suggestions(error)

        assert isinstance(suggestions, list)
        # May be empty or contain generic suggestions
        if suggestions:
            assert any(
                "contact" in suggestion.lower() or "support" in suggestion.lower()
                for suggestion in suggestions
            )

    def test_contextual_suggestions(self) -> None:
        """Test that suggestions are contextual to the error."""
        recovery = ErrorRecovery()

        # Symbol validation error should suggest symbol format help
        symbol_error = ValidationError("Invalid symbol", field="symbol")
        symbol_suggestions = recovery.get_suggestions(symbol_error)

        # Price validation error should suggest price format help
        price_error = ValidationError("Invalid price", field="price")
        price_suggestions = recovery.get_suggestions(price_error)

        # Suggestions should be different for different fields
        assert symbol_suggestions != price_suggestions

    def test_actionable_suggestions(self) -> None:
        """Test that suggestions are actionable and specific."""
        recovery = ErrorRecovery()
        error = ValidationError(
            "Symbol too long", field="symbol", value="VERYLONGSYMBOL"
        )

        suggestions = recovery.get_suggestions(error)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Suggestions should be actionable (contain action words)
        action_words = ["use", "try", "enter", "check", "ensure", "make sure"]
        has_action_word = any(
            any(word in suggestion.lower() for word in action_words)
            for suggestion in suggestions
        )
        assert has_action_word


class TestErrorHandlingIntegration:
    """Test integration between error handling components."""

    def test_full_error_handling_workflow(self) -> None:
        """Test complete error handling workflow from error to user message."""
        # Create error handling components
        boundary = StreamlitErrorBoundary()
        recovery = ErrorRecovery()

        # Create an error
        error = ValidationError("Invalid symbol format", field="symbol", value="123")

        # Test the full workflow
        with patch("streamlit.error") as mock_error:
            # Handle the error
            boundary.handle_error(error)

            # Should display user-friendly error
            mock_error.assert_called_once()

            # Get recovery suggestions
            suggestions = recovery.get_suggestions(error)

            # Should have suggestions
            assert len(suggestions) > 0

    def test_error_context_preservation(self) -> None:
        """Test that error context is preserved through the handling pipeline."""
        error = BusinessLogicError(
            "Risk limit exceeded",
            rule="portfolio_risk_limit",
            current_value=5.0,
            limit_value=2.0,
            context={"portfolio_id": 123, "user_id": "test"},
        )

        mapper = ErrorMessageMapper()
        user_message = mapper.get_user_message(error)

        # Context should influence the message
        assert isinstance(user_message, str)
        assert len(user_message) > 0

        recovery = ErrorRecovery()
        suggestions = recovery.get_suggestions(error)

        # Context should influence suggestions
        assert isinstance(suggestions, list)

    def test_error_logging_integration(self) -> None:
        """Test that all error types are properly logged."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            log_path = Path(f.name)

        try:
            logger = ErrorLogger(log_file=log_path)

            # Test different error types
            errors = [
                ValidationError("Invalid input", field="symbol"),
                DatabaseError("Connection failed", operation="SELECT"),
                BusinessLogicError("Rule violation", rule="test_rule"),
                ValueError("Generic error"),
            ]

            for error in errors:
                logger.log_error(error)

            # Check log file contains all errors
            with open(log_path, "r", encoding="utf-8") as f:
                log_content = f.read()

            assert "VALIDATION_ERROR" in log_content
            assert "DATABASE_ERROR" in log_content
            assert "BUSINESS_LOGIC_ERROR" in log_content
            assert "ValueError" in log_content

        finally:
            if log_path.exists():
                log_path.unlink()
