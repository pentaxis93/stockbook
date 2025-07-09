"""Tests for domain exception handler middleware.

Tests the mapping of domain exceptions to appropriate HTTP responses.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions.base import (
    AlreadyExistsError,
    BusinessRuleViolationError,
    DomainError,
    NotFoundError,
)
from src.presentation.web.middleware.exception_handler import (
    already_exists_exception_handler,
    business_rule_violation_exception_handler,
    domain_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    not_found_exception_handler,
)


class TestNotFoundExceptionHandler:
    """Test handling of NotFoundError exceptions."""

    @pytest.mark.anyio
    async def test_not_found_exception_returns_404(self) -> None:
        """Should return 404 HTTP response for NotFoundError."""
        # Arrange
        request = Mock(spec=Request)
        exception = NotFoundError(entity_type="Stock", identifier="AAPL")

        # Act
        response = await not_found_exception_handler(request, exception)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
        assert response.body == b'{"detail":"Stock with identifier \'AAPL\' not found"}'

    @pytest.mark.anyio
    async def test_not_found_with_custom_message(self) -> None:
        """Should handle NotFoundError with custom entity and identifier."""
        # Arrange
        request = Mock(spec=Request)
        exception = NotFoundError(entity_type="Portfolio", identifier="portfolio-123")

        # Act
        response = await not_found_exception_handler(request, exception)

        # Assert
        assert response.status_code == 404
        assert (
            response.body
            == b'{"detail":"Portfolio with identifier \'portfolio-123\' not found"}'
        )


class TestAlreadyExistsExceptionHandler:
    """Test handling of AlreadyExistsError exceptions."""

    @pytest.mark.anyio
    async def test_already_exists_returns_409(self) -> None:
        """Should return 409 Conflict for AlreadyExistsError."""
        # Arrange
        request = Mock(spec=Request)
        exception = AlreadyExistsError(entity_type="Stock", identifier="MSFT")

        # Act
        response = await already_exists_exception_handler(request, exception)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 409
        assert (
            response.body
            == b'{"detail":"Stock with identifier \'MSFT\' already exists"}'
        )

    @pytest.mark.anyio
    async def test_already_exists_with_portfolio(self) -> None:
        """Should handle AlreadyExistsError for portfolio entities."""
        # Arrange
        request = Mock(spec=Request)
        exception = AlreadyExistsError(
            entity_type="Portfolio",
            identifier="Growth Portfolio",
        )

        # Act
        response = await already_exists_exception_handler(request, exception)

        # Assert
        assert response.status_code == 409
        expected = (
            b'{"detail":"Portfolio with identifier \'Growth Portfolio\' '
            b'already exists"}'
        )
        assert response.body == expected


class TestBusinessRuleViolationExceptionHandler:
    """Test handling of BusinessRuleViolationError exceptions."""

    @pytest.mark.anyio
    async def test_business_rule_violation_returns_422(self) -> None:
        """Should return 422 Unprocessable Entity for BusinessRuleViolationError."""
        # Arrange
        request = Mock(spec=Request)
        exception = BusinessRuleViolationError(
            rule="portfolio_must_be_active",
            context={"portfolio_id": "portfolio-123", "operation": "modify"},
        )

        # Act
        response = await business_rule_violation_exception_handler(request, exception)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 422
        expected_detail = (
            "Business rule 'portfolio_must_be_active' violated. "
            "Context: {'portfolio_id': 'portfolio-123', 'operation': 'modify'}"
        )
        assert response.body == f'{{"detail":"{expected_detail}"}}'.encode()

    @pytest.mark.anyio
    async def test_business_rule_violation_with_balance_error(self) -> None:
        """Should handle balance-related business rule violations."""
        # Arrange
        request = Mock(spec=Request)
        exception = BusinessRuleViolationError(
            rule="sufficient_portfolio_balance",
            context={
                "portfolio_id": "portfolio-456",
                "required_amount": 10000.0,
                "available_amount": 5000.0,
                "shortfall": 5000.0,
            },
        )

        # Act
        response = await business_rule_violation_exception_handler(request, exception)

        # Assert
        assert response.status_code == 422
        assert b"sufficient_portfolio_balance" in response.body
        assert b"required_amount" in response.body


class TestDomainExceptionHandler:
    """Test handling of generic DomainError exceptions."""

    @pytest.mark.anyio
    async def test_domain_exception_returns_400(self) -> None:
        """Should return 400 Bad Request for generic DomainError."""
        # Arrange
        request = Mock(spec=Request)
        exception = DomainError("Invalid operation on domain entity")

        # Act
        response = await domain_exception_handler(request, exception)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert response.body == b'{"detail":"Invalid operation on domain entity"}'

    @pytest.mark.anyio
    async def test_domain_exception_with_custom_message(self) -> None:
        """Should preserve custom message in DomainError."""
        # Arrange
        request = Mock(spec=Request)
        custom_message = "Cannot perform this action due to domain constraints"
        exception = DomainError(custom_message)

        # Act
        response = await domain_exception_handler(request, exception)

        # Assert
        assert response.status_code == 400
        assert response.body == f'{{"detail":"{custom_message}"}}'.encode()


class TestHTTPExceptionHandler:
    """Test handling of HTTPException pass-through."""

    @pytest.mark.anyio
    async def test_http_exception_passes_through(self) -> None:
        """Should pass through HTTPException without modification."""
        # Arrange
        request = Mock(spec=Request)
        exception = HTTPException(status_code=403, detail="Forbidden resource")

        # Act
        response = await http_exception_handler(request, exception)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 403
        assert response.body == b'{"detail":"Forbidden resource"}'

    @pytest.mark.anyio
    async def test_http_exception_preserves_all_fields(self) -> None:
        """Should preserve all fields of HTTPException."""
        # Arrange
        request = Mock(spec=Request)
        headers = {"X-Custom-Header": "value"}
        exception = HTTPException(
            status_code=401,
            detail="Authentication required",
            headers=headers,
        )

        # Act
        response = await http_exception_handler(request, exception)

        # Assert
        assert response.status_code == 401
        assert response.body == b'{"detail":"Authentication required"}'
        # Headers are set on the response
        assert response.headers.get("X-Custom-Header") == "value"


class TestGenericExceptionHandler:
    """Test handling of unexpected exceptions."""

    @patch("src.presentation.web.middleware.exception_handler.logger")
    @pytest.mark.anyio
    async def test_unexpected_exception_returns_500(self, mock_logger: Mock) -> None:
        """Should return 500 Internal Server Error for unexpected exceptions."""
        # Arrange
        request = Mock(spec=Request)
        request.url.path = "/api/v1/stocks"
        exception = RuntimeError("Database connection lost")

        # Act
        response = await generic_exception_handler(request, exception)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert response.body == b'{"detail":"An unexpected error occurred"}'

        # Verify logging
        mock_logger.exception.assert_called_once_with(
            "Unexpected error at %s: %s",
            "/api/v1/stocks",
            "Database connection lost",
        )

    @patch("src.presentation.web.middleware.exception_handler.logger")
    @pytest.mark.anyio
    async def test_unexpected_exception_logs_details(self, mock_logger: Mock) -> None:
        """Should log exception details for debugging."""
        # Arrange
        request = Mock(spec=Request)
        request.url.path = "/api/v1/portfolios/123"
        exception = ValueError("Invalid portfolio state")

        # Act
        response = await generic_exception_handler(request, exception)

        # Assert
        assert response.status_code == 500
        mock_logger.exception.assert_called_once_with(
            "Unexpected error at %s: %s",
            "/api/v1/portfolios/123",
            "Invalid portfolio state",
        )


class TestExceptionResponseFormat:
    """Test that all exception handlers follow consistent response format."""

    @pytest.mark.anyio
    async def test_all_responses_have_detail_field(self) -> None:
        """Should ensure all error responses have 'detail' field."""
        request = Mock(spec=Request)
        request.url.path = "/test"

        # Test each exception type
        test_cases = [
            (
                NotFoundError(entity_type="Test", identifier="123"),
                not_found_exception_handler,
            ),
            (
                AlreadyExistsError(entity_type="Test", identifier="456"),
                already_exists_exception_handler,
            ),
            (
                BusinessRuleViolationError(rule="test_rule", context={}),
                business_rule_violation_exception_handler,
            ),
            (
                DomainError("Test domain error"),
                domain_exception_handler,
            ),
            (
                HTTPException(status_code=400, detail="Test HTTP error"),
                http_exception_handler,
            ),
            (
                RuntimeError("Test runtime error"),
                generic_exception_handler,
            ),
        ]

        for exception, handler in test_cases:
            # Suppress logger for generic handler
            if handler == generic_exception_handler:
                with patch("src.presentation.web.middleware.exception_handler.logger"):
                    response = await handler(request, exception)
            else:
                response = await handler(request, exception)

            # All responses should have 'detail' field
            assert (
                b'"detail":' in response.body
            ), f"Handler {handler.__name__} missing detail field"

    @pytest.mark.anyio
    async def test_response_content_type_is_json(self) -> None:
        """Should ensure all responses have JSON content type."""
        request = Mock(spec=Request)

        # Test a sample handler
        exception = NotFoundError(entity_type="Test", identifier="123")
        response = await not_found_exception_handler(request, exception)

        # Check content type
        assert response.media_type == "application/json"


class TestExceptionHandlerTypeGuards:
    """Test the type guard error handling in exception handlers."""

    @pytest.mark.anyio
    async def test_not_found_handler_with_wrong_exception_type(self) -> None:
        """Should raise TypeError if wrong exception type is passed."""
        request = Mock(spec=Request)
        wrong_exception = ValueError("Not a NotFoundError")

        with pytest.raises(
            TypeError,
            match="Expected NotFoundError but got ValueError",
        ):
            _ = await not_found_exception_handler(request, wrong_exception)

    @pytest.mark.anyio
    async def test_already_exists_handler_with_wrong_exception_type(self) -> None:
        """Should raise TypeError if wrong exception type is passed."""
        request = Mock(spec=Request)
        wrong_exception = RuntimeError("Not an AlreadyExistsError")

        with pytest.raises(
            TypeError,
            match="Expected AlreadyExistsError but got RuntimeError",
        ):
            _ = await already_exists_exception_handler(request, wrong_exception)

    @pytest.mark.anyio
    async def test_business_rule_handler_with_wrong_exception_type(self) -> None:
        """Should raise TypeError if wrong exception type is passed."""
        request = Mock(spec=Request)
        wrong_exception = KeyError("Not a BusinessRuleViolationError")

        with pytest.raises(
            TypeError,
            match="Expected BusinessRuleViolationError but got KeyError",
        ):
            _ = await business_rule_violation_exception_handler(
                request,
                wrong_exception,
            )

    @pytest.mark.anyio
    async def test_domain_handler_with_wrong_exception_type(self) -> None:
        """Should raise TypeError if wrong exception type is passed."""
        request = Mock(spec=Request)
        wrong_exception = AttributeError("Not a DomainError")

        with pytest.raises(
            TypeError,
            match="Expected DomainError but got AttributeError",
        ):
            _ = await domain_exception_handler(request, wrong_exception)

    @pytest.mark.anyio
    async def test_http_handler_with_wrong_exception_type(self) -> None:
        """Should raise TypeError if wrong exception type is passed."""
        request = Mock(spec=Request)
        wrong_exception = IndexError("Not an HTTPException")

        with pytest.raises(
            TypeError,
            match="Expected HTTPException but got IndexError",
        ):
            _ = await http_exception_handler(request, wrong_exception)


class TestExceptionHandlerIntegration:
    """Integration tests for exception handlers."""

    @pytest.mark.parametrize(
        ("exception", "expected_status", "expected_detail_contains"),
        [
            (
                NotFoundError(entity_type="Stock", identifier="INVALID"),
                404,
                "Stock with identifier 'INVALID' not found",
            ),
            (
                AlreadyExistsError(entity_type="Stock", identifier="AAPL"),
                409,
                "Stock with identifier 'AAPL' already exists",
            ),
            (
                BusinessRuleViolationError(
                    rule="invalid_grade",
                    context={"grade": "Z"},
                ),
                422,
                "Business rule 'invalid_grade' violated",
            ),
            (
                DomainError("Invalid domain operation"),
                400,
                "Invalid domain operation",
            ),
            (
                HTTPException(status_code=401, detail="Unauthorized"),
                401,
                "Unauthorized",
            ),
        ],
    )
    @pytest.mark.anyio
    async def test_exception_handlers_with_various_inputs(
        self,
        exception: Exception,
        expected_status: int,
        expected_detail_contains: str,
    ) -> None:
        """Should handle various exception types correctly."""
        request = Mock(spec=Request)
        request.url.path = "/test"

        # Map exception types to handlers
        handler_map = {
            NotFoundError: not_found_exception_handler,
            AlreadyExistsError: already_exists_exception_handler,
            BusinessRuleViolationError: business_rule_violation_exception_handler,
            DomainError: domain_exception_handler,
            HTTPException: http_exception_handler,
        }

        handler = handler_map.get(type(exception))  # type: ignore[arg-type]
        assert handler is not None, f"No handler for {type(exception)}"

        response = await handler(request, exception)

        assert response.status_code == expected_status
        assert expected_detail_contains.encode() in response.body
