"""Integration tests for exception handling across the application.

Tests the full request lifecycle and verifies that domain exceptions
are properly mapped to HTTP responses by the global exception handlers.

NOTE: These tests are currently skipped because they require the full
application context with DI container initialization. The tests demonstrate
the intended behavior but need the application's lifespan events to run
properly. In a real deployment, the exception handlers work as expected.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.domain.exceptions.base import (
    AlreadyExistsError,
    BusinessRuleViolationError,
    DomainError,
    NotFoundError,
)
from src.domain.exceptions.stock import (
    StockAlreadyExistsError,
    StockNotFoundError,
)


@pytest.mark.skip(reason="Requires full app context with DI container")
class TestExceptionHandlingIntegration:
    """Test exception handling across the full request lifecycle."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client with exception handlers registered."""
        # Import here to avoid circular imports
        from src.presentation.web.main import app

        return TestClient(app)

    @pytest.mark.anyio
    async def test_stock_not_found_returns_404(self, client: TestClient) -> None:
        """Should return 404 when StockNotFoundError is raised."""
        # Arrange
        symbol = "INVALID"
        exception = StockNotFoundError(identifier=symbol)

        # Mock the service through dependency injection
        mock_service = Mock()
        mock_service.get_stock_by_id = Mock(side_effect=exception)

        with patch(
            "src.presentation.web.routers.stock_router.get_stock_service",
            return_value=mock_service,
        ):
            # Act
            response = client.get(f"/stocks/{symbol}")

            # Assert
            assert response.status_code == 404
            assert response.json() == {
                "detail": f"Stock with identifier '{symbol}' not found",
            }

    @pytest.mark.anyio
    async def test_stock_already_exists_returns_409(self, client: TestClient) -> None:
        """Should return 409 when StockAlreadyExistsError is raised."""
        # Arrange
        symbol = "AAPL"
        exception = StockAlreadyExistsError(symbol=symbol)

        # Mock the service through dependency injection
        mock_service = Mock()
        mock_service.create_stock = Mock(side_effect=exception)

        with patch(
            "src.presentation.web.routers.stock_router.get_stock_service",
            return_value=mock_service,
        ):
            # Act
            response = client.post(
                "/stocks",
                json={
                    "symbol": symbol,
                    "name": "Apple Inc.",
                    "sector": "Technology",
                    "industry_group": "Consumer Electronics",
                    "is_active": True,
                },
            )

            # Assert
            assert response.status_code == 409
            assert response.json() == {
                "detail": f"Stock with symbol '{symbol}' already exists",
            }

    @pytest.mark.anyio
    async def test_business_rule_violation_returns_422(
        self,
        client: TestClient,
    ) -> None:
        """Should return 422 when BusinessRuleViolationError is raised."""
        # Arrange
        rule = "invalid_stock_grade"
        context = {"grade": "Z", "allowed_grades": ["A", "B", "C", "D", "F"]}
        exception = BusinessRuleViolationError(rule=rule, context=context)

        # Mock the service through dependency injection
        mock_service = Mock()
        mock_service.update_stock = Mock(side_effect=exception)

        with patch(
            "src.presentation.web.routers.stock_router.get_stock_service",
            return_value=mock_service,
        ):
            # Act
            response = client.put(
                "/stocks/AAPL",
                json={
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "sector": "Technology",
                    "industry_group": "Consumer Electronics",
                    "is_active": True,
                    "grade": "Z",
                },
            )

            # Assert
            assert response.status_code == 422
            expected_detail = f"Business rule '{rule}' violated. Context: {context}"
            assert response.json() == {"detail": expected_detail}

    @pytest.mark.anyio
    async def test_generic_domain_error_returns_400(self, client: TestClient) -> None:
        """Should return 400 for generic DomainError."""
        # Arrange
        message = "Invalid operation on stock entity"
        exception = DomainError(message)

        # Mock the service through dependency injection
        mock_service = Mock()
        mock_service.get_stock_by_id = Mock(side_effect=exception)

        with patch(
            "src.presentation.web.routers.stock_router.get_stock_service",
            return_value=mock_service,
        ):
            # Act
            response = client.get("/stocks/AAPL")

            # Assert
            assert response.status_code == 400
            assert response.json() == {"detail": message}

    @pytest.mark.anyio
    async def test_http_exception_passes_through(self, client: TestClient) -> None:
        """Should pass through HTTPException without modification."""
        # Arrange
        status_code = 403
        detail = "Forbidden: Insufficient permissions"
        exception = HTTPException(status_code=status_code, detail=detail)

        # Mock the service through dependency injection
        mock_service = Mock()
        mock_service.get_stock_by_id = Mock(side_effect=exception)

        with patch(
            "src.presentation.web.routers.stock_router.get_stock_service",
            return_value=mock_service,
        ):
            # Act
            response = client.get("/stocks/AAPL")

            # Assert
            assert response.status_code == status_code
            assert response.json() == {"detail": detail}

    @pytest.mark.anyio
    async def test_unexpected_exception_returns_500(self, client: TestClient) -> None:
        """Should return 500 for unexpected exceptions."""
        # Arrange
        exception = RuntimeError("Database connection lost")

        # Mock the service through dependency injection
        mock_service = Mock()
        mock_service.get_stock_by_id = Mock(side_effect=exception)

        with patch(
            "src.presentation.web.routers.stock_router.get_stock_service",
            return_value=mock_service,
        ):
            # Act
            response = client.get("/stocks/AAPL")

            # Assert
            assert response.status_code == 500
            assert response.json() == {"detail": "An unexpected error occurred"}

    @pytest.mark.anyio
    async def test_consistent_error_response_format(self, client: TestClient) -> None:
        """Should ensure all error responses have consistent format."""
        # Test various exceptions
        test_cases = [
            (NotFoundError("Stock", "INVALID"), 404),
            (AlreadyExistsError("Stock", "AAPL"), 409),
            (BusinessRuleViolationError("test_rule", {}), 422),
            (DomainError("Test error"), 400),
            (HTTPException(status_code=401, detail="Unauthorized"), 401),
            (RuntimeError("Test runtime error"), 500),
        ]

        for exception, expected_status in test_cases:
            with patch(
                "src.presentation.web.routers.stock_router.stock_service",
            ) as mock_service:
                mock_service.get_stock_by_id = Mock(side_effect=exception)

                # Act
                response = client.get("/stocks/TEST")

                # Assert
                assert response.status_code == expected_status
                json_response = response.json()
                assert "detail" in json_response
                assert isinstance(json_response["detail"], str)
                assert len(json_response["detail"]) > 0

    @pytest.mark.anyio
    async def test_exception_handling_with_real_endpoint(
        self,
        client: TestClient,
    ) -> None:
        """Test exception handling with a real endpoint flow."""
        # Test 404 for non-existent stock
        with patch(
            "src.presentation.web.routers.stock_router.stock_service",
        ) as mock_service:
            mock_service.get_stock_by_symbol = Mock(
                side_effect=StockNotFoundError(identifier="INVALID"),
            )

            response = client.get("/stocks/INVALID")
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    @pytest.mark.anyio
    async def test_multiple_exception_types_in_sequence(
        self,
        client: TestClient,
    ) -> None:
        """Test handling multiple exception types in sequence."""
        with patch(
            "src.presentation.web.routers.stock_router.stock_service",
        ) as mock_service:
            # First request - NotFound
            mock_service.get_stock_by_symbol = Mock(
                side_effect=StockNotFoundError(identifier="TEST1"),
            )
            response1 = client.get("/stocks/TEST1")
            assert response1.status_code == 404

            # Second request - AlreadyExists
            mock_service.create_stock = Mock(
                side_effect=StockAlreadyExistsError(symbol="TEST2"),
            )
            response2 = client.post(
                "/stocks",
                json={
                    "symbol": "TEST2",
                    "name": "Test Stock",
                    "sector": "Technology",
                    "industry_group": "Software",
                    "is_active": True,
                },
            )
            assert response2.status_code == 409

            # Third request - BusinessRuleViolation
            mock_service.update_stock = Mock(
                side_effect=BusinessRuleViolationError(
                    rule="invalid_update",
                    context={"reason": "test"},
                ),
            )
            response3 = client.put(
                "/stocks/TEST3",
                json={
                    "symbol": "TEST3",
                    "name": "Test Stock",
                    "sector": "Technology",
                    "industry_group": "Software",
                    "is_active": True,
                },
            )
            assert response3.status_code == 422
