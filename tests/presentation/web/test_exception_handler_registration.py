"""Unit tests for exception handler registration in the main application."""

from src.domain.exceptions.base import (
    AlreadyExistsError,
    BusinessRuleViolationError,
    DomainError,
    NotFoundError,
)
from src.presentation.web.main import app


class TestExceptionHandlerRegistration:
    """Test that exception handlers are properly registered in the main app."""

    def test_exception_handlers_are_registered(self) -> None:
        """Verify that all domain exception handlers are registered."""
        # Get the exception handlers from the app
        exception_handlers = app.exception_handlers

        # Check that our domain exceptions are registered
        assert NotFoundError in exception_handlers
        assert AlreadyExistsError in exception_handlers
        assert BusinessRuleViolationError in exception_handlers
        assert DomainError in exception_handlers
        assert Exception in exception_handlers

    def test_exception_handler_count(self) -> None:
        """Verify the expected number of exception handlers."""
        # Get the exception handlers from the app
        exception_handlers = app.exception_handlers

        # We should have at least our 5 custom handlers
        # (NotFoundError, AlreadyExistsError, BusinessRuleViolationError,
        #  DomainError, Exception)
        assert len(exception_handlers) >= 5

    def test_handler_functions_are_correct(self) -> None:
        """Verify that the correct handler functions are registered."""
        from src.presentation.web.middleware.exception_handler import (
            already_exists_exception_handler,
            business_rule_violation_exception_handler,
            domain_exception_handler,
            generic_exception_handler,
            not_found_exception_handler,
        )

        # Get the exception handlers from the app
        exception_handlers = app.exception_handlers

        # Check that the correct handler functions are registered
        assert exception_handlers[NotFoundError] == not_found_exception_handler
        assert (
            exception_handlers[AlreadyExistsError] == already_exists_exception_handler
        )
        assert (
            exception_handlers[BusinessRuleViolationError]
            == business_rule_violation_exception_handler
        )
        assert exception_handlers[DomainError] == domain_exception_handler
        assert exception_handlers[Exception] == generic_exception_handler
