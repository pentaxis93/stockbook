"""
Tests for Stock View Models in presentation layer.

Following TDD approach - these tests define the expected behavior
of view models for data transfer between UI and controllers.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest

from src.application.dto.stock_dto import StockDto
from src.presentation.view_models.stock_view_models import (
    CreateStockRequest,
    CreateStockResponse,
    StockDetailResponse,
    StockListResponse,
    StockSearchRequest,
    StockViewModel,
    UpdateStockRequest,
    UpdateStockResponse,
    ValidationErrorResponse,
)


class TestCreateStockRequest:
    """Test suite for CreateStockRequest view model."""

    def test_create_stock_request_initialization(self):
        """Should initialize with all required fields."""
        # Act
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="High quality stock",
        )

        # Assert
        assert request.symbol == "AAPL"
        assert request.name == "Apple Inc."
        assert request.sector == "Technology"
        assert request.industry_group == "Software"
        assert request.grade == "A"
        assert request.notes == "High quality stock"

    def test_create_stock_request_minimal_fields(self):
        """Should initialize with minimal required fields."""
        # Act
        request = CreateStockRequest(symbol="AAPL", name="Apple Inc.")

        # Assert
        assert request.symbol == "AAPL"
        assert request.name == "Apple Inc."
        assert request.industry_group is None
        assert request.grade is None
        assert request.notes == ""

    def test_create_stock_request_validation_rules(self):
        """Should define validation rules for fields."""
        # Act
        request = CreateStockRequest(symbol="AAPL", name="Apple Inc.")

        # Assert
        assert hasattr(request, "validate")
        assert hasattr(request, "to_command")

    def test_create_stock_request_to_command_conversion(self):
        """Should convert to application command correctly."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Test notes",
        )

        # Act
        command = request.to_command()

        # Assert
        assert command.symbol == "AAPL"
        assert command.name == "Apple Inc."
        assert command.sector == "Technology"
        assert command.industry_group == "Software"
        assert command.grade == "A"
        assert command.notes == "Test notes"

    def test_create_stock_request_validation_success(self):
        """Should validate successfully with valid data."""
        # Arrange
        request = CreateStockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes="",
        )

        # Act
        errors = request.validate()

        # Assert
        assert not errors

    def test_create_stock_request_validation_empty_symbol(self):
        """Should validate symbol is not empty."""
        # Arrange
        request = CreateStockRequest(symbol="", name="Apple Inc.")

        # Act
        errors = request.validate()

        # Assert
        assert "symbol" in errors
        assert "Stock symbol cannot be empty" in errors["symbol"]

    def test_create_stock_request_validation_empty_name(self):
        """Should validate name is not empty."""
        # Arrange
        request = CreateStockRequest(symbol="AAPL", name="")

        # Act
        errors = request.validate()

        # Assert
        assert "name" in errors
        assert "Stock name cannot be empty" in errors["name"]

    def test_create_stock_request_validation_invalid_symbol_format(self):
        """Should validate symbol format."""
        # Arrange
        request = CreateStockRequest(symbol="invalid123", name="Test Company")

        # Act
        errors = request.validate()

        # Assert
        assert "symbol" in errors
        assert "Invalid stock symbol format" in errors["symbol"]

    def test_create_stock_request_validation_invalid_grade(self):
        """Should validate grade values."""
        # Arrange
        request = CreateStockRequest(symbol="AAPL", name="Apple Inc.", grade="Z")

        # Act
        errors = request.validate()

        # Assert
        assert "grade" in errors
        assert "Grade must be A, B, C, or empty" in errors["grade"]

    def test_create_stock_request_validation_name_too_long(self):
        """Should validate name length."""
        # Arrange
        long_name = "A" * 201  # Exceeds max length
        request = CreateStockRequest(symbol="AAPL", name=long_name)

        # Act
        errors = request.validate()

        # Assert
        assert "name" in errors
        assert "Name cannot exceed 200 characters" in errors["name"]

    def test_create_stock_request_sanitization(self):
        """Should sanitize input data."""
        # Arrange
        request = CreateStockRequest(
            symbol="  aapl  ",
            name="  Apple Inc.  ",
            industry_group="  Technology  ",
            grade="a",
            notes="  Some notes  ",
        )

        # Act
        sanitized = request.sanitize()

        # Assert
        assert sanitized.symbol == "AAPL"
        assert sanitized.name == "Apple Inc."
        assert sanitized.industry_group == "Technology"
        assert sanitized.grade == "A"
        assert sanitized.notes == "Some notes"


class TestStockViewModel:
    """Test suite for StockViewModel."""

    def test_stock_view_model_from_dto(self):
        """Should create view model from DTO."""
        # Arrange
        dto = StockDto(
            id="stock-id-1",
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes="High quality stock",
        )

        # Act
        view_model = StockViewModel.from_dto(dto)

        # Assert
        assert view_model.id == "stock-id-1"
        assert view_model.symbol == "AAPL"
        assert view_model.name == "Apple Inc."
        assert view_model.industry_group == "Technology"
        assert view_model.grade == "A"
        assert view_model.notes == "High quality stock"
        assert view_model.display_name == "AAPL - Apple Inc."

    def test_stock_view_model_display_properties(self):
        """Should provide computed display properties."""
        # Arrange
        dto = StockDto(
            id="stock-id-1",
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes="",
        )

        # Act
        view_model = StockViewModel.from_dto(dto)

        # Assert
        assert view_model.display_name == "AAPL - Apple Inc."
        assert view_model.grade_display == "Grade A"
        assert view_model.has_notes is False
        assert view_model.is_high_grade is True

    def test_stock_view_model_grade_display_formatting(self):
        """Should format grade display correctly."""
        # Test Grade A
        dto_a = StockDto(id="stock-id-1", symbol="AAPL", name="Apple Inc.", grade="A")
        view_model_a = StockViewModel.from_dto(dto_a)
        assert view_model_a.grade_display == "Grade A"
        assert view_model_a.is_high_grade is True

        # Test Grade B
        dto_b = StockDto(id="stock-id-2", symbol="MSFT", name="Microsoft", grade="B")
        view_model_b = StockViewModel.from_dto(dto_b)
        assert view_model_b.grade_display == "Grade B"
        assert view_model_b.is_high_grade is False

        # Test No Grade
        dto_none = StockDto(
            id="stock-id-3", symbol="TEST", name="Test Corp", grade=None
        )
        view_model_none = StockViewModel.from_dto(dto_none)
        assert view_model_none.grade_display == "No Grade"
        assert view_model_none.is_high_grade is False

    def test_stock_view_model_notes_handling(self):
        """Should handle notes properly."""
        # With notes
        dto_with_notes = StockDto(
            id="stock-id-1", symbol="AAPL", name="Apple Inc.", notes="Good stock"
        )
        view_model_with = StockViewModel.from_dto(dto_with_notes)
        assert view_model_with.has_notes is True
        assert view_model_with.notes_preview == "Good stock"

        # Without notes
        dto_no_notes = StockDto(
            id="stock-id-2", symbol="MSFT", name="Microsoft", notes=""
        )
        view_model_without = StockViewModel.from_dto(dto_no_notes)
        assert view_model_without.has_notes is False
        assert view_model_without.notes_preview == "No notes"

    def test_stock_view_model_long_notes_preview(self):
        """Should truncate long notes for preview."""
        # Arrange
        long_notes = "This is a very long note that exceeds the preview limit " * 5
        dto = StockDto(
            id="stock-id-1", symbol="AAPL", name="Apple Inc.", notes=long_notes
        )

        # Act
        view_model = StockViewModel.from_dto(dto)

        # Assert
        assert len(view_model.notes_preview) <= 100
        assert view_model.notes_preview.endswith("...")


class TestStockListResponse:
    """Test suite for StockListResponse."""

    def test_stock_list_response_success(self):
        """Should create successful response with stock list."""
        # Arrange
        stocks = [
            StockViewModel(
                id="stock-id-1", symbol="AAPL", name="Apple Inc.", grade="A"
            ),
            StockViewModel(
                id="stock-id-2", symbol="GOOGL", name="Alphabet Inc.", grade="A"
            ),
        ]

        # Act
        response = StockListResponse.create_success(stocks, "Retrieved successfully")

        # Assert
        assert response.success is True
        assert len(response.stocks) == 2
        assert response.total_count == 2
        assert response.message == "Retrieved successfully"
        assert response.errors is None

    def test_stock_list_response_empty(self):
        """Should handle empty stock list."""
        # Act
        response = StockListResponse.create_success([], "No stocks found")

        # Assert
        assert response.success is True
        assert len(response.stocks) == 0
        assert response.total_count == 0
        assert response.message == "No stocks found"

    def test_stock_list_response_error(self):
        """Should create error response."""
        # Act
        response = StockListResponse.create_error("Database error")

        # Assert
        assert response.success is False
        assert response.stocks == []
        assert response.total_count == 0
        assert response.message == "Database error"

    def test_stock_list_response_filtering_info(self):
        """Should include filtering information."""
        # Arrange
        stocks = [
            StockViewModel(id="stock-id-1", symbol="AAPL", name="Apple Inc.", grade="A")
        ]

        # Act
        response = StockListResponse.create_success(
            stocks, "Filtered results", filters_applied={"grade": "A"}
        )

        # Assert
        assert response.filters_applied == {"grade": "A"}
        assert response.has_filters is True


class TestCreateStockResponse:
    """Test suite for CreateStockResponse."""

    def test_create_stock_response_success(self):
        """Should create successful response."""
        # Act
        response = CreateStockResponse.create_success(
            stock_id="stock-id-1", symbol="AAPL", message="Stock created successfully"
        )

        # Assert
        assert response.success is True
        assert response.stock_id == "stock-id-1"
        assert response.symbol == "AAPL"
        assert response.message == "Stock created successfully"
        assert response.errors is None

    def test_create_stock_response_error(self):
        """Should create error response."""
        # Act
        response = CreateStockResponse.create_error("Stock already exists")

        # Assert
        assert response.success is False
        assert response.stock_id is None
        assert response.symbol is None
        assert response.message == "Stock already exists"
        assert response.errors is None


class TestValidationErrorResponse:
    """Test suite for ValidationErrorResponse."""

    def test_validation_error_response_single_error(self):
        """Should handle single validation error."""
        # Arrange
        errors = {"symbol": "Invalid symbol format"}

        # Act
        response = ValidationErrorResponse(errors)

        # Assert
        assert response.success is False
        assert response.errors == errors
        assert response.message == "Validation failed"
        assert response.error_count == 1

    def test_validation_error_response_multiple_errors(self):
        """Should handle multiple validation errors."""
        # Arrange
        errors = {
            "symbol": "Invalid symbol format",
            "name": "Name cannot be empty",
            "grade": "Invalid grade value",
        }

        # Act
        response = ValidationErrorResponse(errors)

        # Assert
        assert response.success is False
        assert response.errors == errors
        assert response.error_count == 3
        assert "3 validation errors" in response.message

    def test_validation_error_response_field_errors_list(self):
        """Should provide list of field errors."""
        # Arrange
        errors = {"symbol": "Invalid symbol format", "name": "Name cannot be empty"}

        # Act
        response = ValidationErrorResponse(errors)

        # Assert
        field_errors = response.field_errors
        assert len(field_errors) == 2
        assert "symbol: Invalid symbol format" in field_errors
        assert "name: Name cannot be empty" in field_errors


class TestStockSearchRequest:
    """Test suite for StockSearchRequest."""

    def test_stock_search_request_initialization(self):
        """Should initialize search request with filters."""
        # Act
        request = StockSearchRequest(
            symbol_filter="AAPL",
            name_filter="Apple",
            grade_filter="A",
            industry_filter="Technology",
        )

        # Assert
        assert request.symbol_filter == "AAPL"
        assert request.name_filter == "Apple"
        assert request.grade_filter == "A"
        assert request.industry_filter == "Technology"

    def test_stock_search_request_has_filters(self):
        """Should detect if any filters are applied."""
        # With filters
        request_with_filters = StockSearchRequest(symbol_filter="AAPL")
        assert request_with_filters.has_filters is True

        # Without filters
        request_no_filters = StockSearchRequest()
        assert request_no_filters.has_filters is False

    def test_stock_search_request_active_filters(self):
        """Should return dictionary of active filters."""
        # Arrange
        request = StockSearchRequest(
            symbol_filter="AAPL",
            grade_filter="A",
            name_filter="",  # Empty filter should be ignored
            industry_filter=None,  # None filter should be ignored
        )

        # Act
        active_filters = request.active_filters

        # Assert
        assert active_filters == {"symbol": "AAPL", "grade": "A"}

    def test_stock_search_request_validation(self):
        """Should validate search parameters."""
        # Valid request
        valid_request = StockSearchRequest(grade_filter="A")
        assert not valid_request.validate()

        # Invalid grade
        invalid_request = StockSearchRequest(grade_filter="Z")
        errors = invalid_request.validate()
        assert "grade_filter" in errors
