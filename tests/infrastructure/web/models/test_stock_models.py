"""
Tests for stock Pydantic models in web presentation layer.

Following TDD principles - these tests define the expected behavior
before implementation.
"""

import pytest
from pydantic import ValidationError


class TestStockRequest:
    """Test suite for StockRequest Pydantic model."""

    def test_stock_request_valid_data(self) -> None:
        """Test StockRequest with valid data."""
        # This test will fail until we implement StockRequest
        from src.infrastructure.web.models.stock_models import StockRequest

        request = StockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="High quality stock",
        )

        assert request.symbol == "AAPL"
        assert request.name == "Apple Inc."
        assert request.sector == "Technology"
        assert request.industry_group == "Software"
        assert request.grade == "A"
        assert request.notes == "High quality stock"

    def test_stock_request_minimal_data(self) -> None:
        """Test StockRequest with only required fields."""
        from src.infrastructure.web.models.stock_models import StockRequest

        request = StockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector=None,
            industry_group=None,
            grade=None,
            notes="",
        )

        assert request.symbol == "AAPL"
        assert request.name == "Apple Inc."
        assert request.sector is None
        assert request.industry_group is None
        assert request.grade is None
        assert request.notes == ""

    def test_stock_request_validation_empty_symbol(self) -> None:
        """Test StockRequest validation fails with empty symbol."""
        from src.infrastructure.web.models.stock_models import StockRequest

        with pytest.raises(ValidationError) as exc_info:
            _ = StockRequest(
                symbol="",
                name="Apple Inc.",
                sector=None,
                industry_group=None,
                grade=None,
                notes="",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("symbol",) for error in errors)

    def test_stock_request_validation_empty_name(self) -> None:
        """Test StockRequest validation fails with empty name."""
        from src.infrastructure.web.models.stock_models import StockRequest

        with pytest.raises(ValidationError) as exc_info:
            _ = StockRequest(
                symbol="AAPL",
                name="",
                sector=None,
                industry_group=None,
                grade=None,
                notes="",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_stock_request_validation_invalid_symbol_format(self) -> None:
        """Test StockRequest validation fails with invalid symbol format."""
        from src.infrastructure.web.models.stock_models import StockRequest

        with pytest.raises(ValidationError) as exc_info:
            _ = StockRequest(
                symbol="123ABC",
                name="Apple Inc.",
                sector=None,
                industry_group=None,
                grade=None,
                notes="",
            )  # numbers not allowed

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("symbol",) for error in errors)

    def test_stock_request_validation_invalid_grade(self) -> None:
        """Test StockRequest validation fails with invalid grade."""
        from src.infrastructure.web.models.stock_models import StockRequest

        with pytest.raises(ValidationError) as exc_info:
            _ = StockRequest(
                symbol="AAPL",
                name="Apple Inc.",
                sector=None,
                industry_group=None,
                grade="D",
                notes="",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("grade",) for error in errors)

    def test_stock_request_symbol_transformation(self) -> None:
        """Test StockRequest automatically transforms symbol to uppercase."""
        from src.infrastructure.web.models.stock_models import StockRequest

        request = StockRequest(
            symbol="aapl",
            name="Apple Inc.",
            sector=None,
            industry_group=None,
            grade=None,
            notes="",
        )
        assert request.symbol == "AAPL"

    def test_stock_request_validation_long_name(self) -> None:
        """Test StockRequest validation fails with name too long."""
        from src.infrastructure.web.models.stock_models import StockRequest

        with pytest.raises(ValidationError) as exc_info:
            _ = StockRequest(
                symbol="AAPL",
                name="A" * 201,  # 201 characters - exceeds 200 limit
                sector=None,
                industry_group=None,
                grade=None,
                notes="",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_stock_request_validation_none_notes(self) -> None:
        """Test StockRequest handles None notes by converting to empty string."""
        from src.infrastructure.web.models.stock_models import StockRequest

        request = StockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector=None,
            industry_group=None,
            grade=None,
            notes=None,
        )

        assert request.notes == ""


class TestStockResponse:
    """Test suite for StockResponse Pydantic model."""

    def test_stock_response_creation(self) -> None:
        """Test StockResponse can be created with full data."""
        from src.infrastructure.web.models.stock_models import StockResponse

        response = StockResponse(
            id="stock-123",
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="High quality stock",
        )

        assert response.id == "stock-123"
        assert response.symbol == "AAPL"
        assert response.name == "Apple Inc."
        assert response.sector == "Technology"
        assert response.industry_group == "Software"
        assert response.grade == "A"
        assert response.notes == "High quality stock"

    def test_stock_response_minimal_data(self) -> None:
        """Test StockResponse with minimal required data."""
        from src.infrastructure.web.models.stock_models import StockResponse

        response = StockResponse(
            id="stock-123",
            symbol="AAPL",
            name="Apple Inc.",
            sector=None,
            industry_group=None,
            grade=None,
            notes="",
        )

        assert response.id == "stock-123"
        assert response.symbol == "AAPL"
        assert response.name == "Apple Inc."
        assert response.sector is None
        assert response.industry_group is None
        assert response.grade is None
        assert response.notes == ""


class TestStockListResponse:
    """Test suite for StockListResponse Pydantic model."""

    def test_stock_list_response_with_stocks(self) -> None:
        """Test StockListResponse with list of stocks."""
        from src.infrastructure.web.models.stock_models import (
            StockListResponse,
            StockResponse,
        )

        stocks = [
            StockResponse(
                id="stock-1",
                symbol="AAPL",
                name="Apple Inc.",
                sector=None,
                industry_group=None,
                grade=None,
                notes="",
            ),
            StockResponse(
                id="stock-2",
                symbol="GOOGL",
                name="Google Inc.",
                sector=None,
                industry_group=None,
                grade=None,
                notes="",
            ),
        ]

        response = StockListResponse(stocks=stocks, total=2)

        assert len(response.stocks) == 2
        assert response.total == 2
        # pylint: disable=unsubscriptable-object
        assert response.stocks[0].symbol == "AAPL"
        assert response.stocks[1].symbol == "GOOGL"

    def test_stock_list_response_empty(self) -> None:
        """Test StockListResponse with empty list."""
        from src.infrastructure.web.models.stock_models import StockListResponse

        response = StockListResponse(stocks=[], total=0)

        assert len(response.stocks) == 0
        assert response.total == 0


class TestErrorResponse:
    """Test suite for ErrorResponse Pydantic model."""

    def test_error_response_creation(self) -> None:
        """Test ErrorResponse can be created."""
        from src.infrastructure.web.models.stock_models import ErrorResponse

        response = ErrorResponse(
            message="Stock not found", code="STOCK_NOT_FOUND", details={"id": "123"}
        )

        assert response.message == "Stock not found"
        assert response.code == "STOCK_NOT_FOUND"
        assert response.details == {"id": "123"}

    def test_error_response_minimal(self) -> None:
        """Test ErrorResponse with minimal data."""
        from src.infrastructure.web.models.stock_models import ErrorResponse

        response = ErrorResponse(message="Error occurred", code=None, details=None)

        assert response.message == "Error occurred"
        assert response.code is None
        assert response.details is None
