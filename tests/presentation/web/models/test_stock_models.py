"""
Tests for Stock Web Models.

Following TDD approach - these tests define the expected behavior
of StockRequest and StockResponse models used in the FastAPI presentation layer.
"""

from typing import Any, Dict

import pytest
from pydantic import ValidationError

from src.application.commands.stock import CreateStockCommand
from src.application.dto.stock_dto import StockDto
from src.presentation.web.models.stock_models import (
    StockListResponse,
    StockRequest,
    StockResponse,
    StockUpdateRequest,
)


class TestStockRequest:
    """Test suite for StockRequest model."""

    def test_create_stock_request_with_all_fields(self) -> None:
        """Should create request with all valid fields."""
        request = StockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Excellent company",
        )

        assert request.symbol == "AAPL"
        assert request.name == "Apple Inc."
        assert request.sector == "Technology"
        assert request.industry_group == "Software"
        assert request.grade == "A"
        assert request.notes == "Excellent company"

    def test_create_stock_request_with_minimal_fields(self) -> None:
        """Should create request with only required fields."""
        request = StockRequest(symbol="MSFT")

        assert request.symbol == "MSFT"
        assert request.name is None
        assert request.sector is None
        assert request.industry_group is None
        assert request.grade is None
        assert request.notes == ""

    def test_create_stock_request_with_name(self) -> None:
        """Should create request with symbol and name."""
        request = StockRequest(symbol="MSFT", name="Microsoft Corp.")

        assert request.symbol == "MSFT"
        assert request.name == "Microsoft Corp."
        assert request.sector is None
        assert request.industry_group is None
        assert request.grade is None
        assert request.notes == ""

    def test_stock_request_normalizes_symbol_to_uppercase(self) -> None:
        """Should normalize symbol to uppercase."""
        request = StockRequest(symbol="aapl", name="Apple Inc.")
        assert request.symbol == "AAPL"

    def test_stock_request_trims_whitespace_from_fields(self) -> None:
        """Should trim whitespace from all string fields."""
        request = StockRequest(
            symbol="  AAPL  ",
            name="  Apple Inc.  ",
            sector="  Technology  ",
            industry_group="  Software  ",
            grade="  A  ",
            notes="  Test notes  ",
        )

        assert request.symbol == "AAPL"
        assert request.name == "Apple Inc."
        assert request.sector == "Technology"
        assert request.industry_group == "Software"
        assert request.grade == "A"
        assert request.notes == "Test notes"

    def test_stock_request_empty_symbol_raises_validation_error(self) -> None:
        """Should raise ValidationError for empty symbol."""
        with pytest.raises(ValidationError) as exc_info:
            _ = StockRequest(symbol="", name="Test Company")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("symbol",)
        assert "Symbol cannot be empty" in errors[0]["msg"]

    def test_stock_request_whitespace_only_symbol_raises_validation_error(self) -> None:
        """Should raise ValidationError for whitespace-only symbol."""
        with pytest.raises(ValidationError) as exc_info:
            _ = StockRequest(symbol="   ", name="Test Company")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("symbol",)
        assert "Symbol cannot be empty" in errors[0]["msg"]

    def test_stock_request_invalid_symbol_format_raises_validation_error(self) -> None:
        """Should raise ValidationError for invalid symbol format."""
        invalid_symbols = [
            "TOOLONG",  # More than 5 characters
            "123",  # Numbers
            "AB-CD",  # Special characters
            "AB CD",  # Spaces
            "ab@cd",  # Special characters
        ]

        for invalid_symbol in invalid_symbols:
            with pytest.raises(ValidationError) as exc_info:
                _ = StockRequest(symbol=invalid_symbol, name="Test Company")

            errors = exc_info.value.errors()
            assert len(errors) == 1
            assert errors[0]["loc"] == ("symbol",)
            # Accept either error message - format or length
            assert any(
                msg in errors[0]["msg"]
                for msg in [
                    "Stock symbol must contain only uppercase letters",
                    "Stock symbol must be between 1 and 5 characters",
                ]
            )

    def test_stock_request_empty_name_becomes_none(self) -> None:
        """Should convert empty name to None."""
        request = StockRequest(symbol="AAPL", name="")
        assert request.name is None

    def test_stock_request_whitespace_only_name_becomes_none(self) -> None:
        """Should convert whitespace-only name to None."""
        request = StockRequest(symbol="AAPL", name="   ")
        assert request.name is None

    def test_stock_request_invalid_grade_raises_validation_error(self) -> None:
        """Should raise ValidationError for invalid grade."""
        with pytest.raises(ValidationError) as exc_info:
            _ = StockRequest(symbol="AAPL", name="Apple Inc.", grade="Z")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("grade",)
        # Pydantic will provide specific error about literal values

    def test_stock_request_grade_normalization(self) -> None:
        """Should normalize grade to uppercase."""
        request = StockRequest(symbol="AAPL", name="Apple Inc.", grade="a")
        assert request.grade == "A"

    def test_stock_request_empty_optional_fields_become_none(self) -> None:
        """Should convert empty optional string fields to None."""
        request = StockRequest(
            symbol="AAPL", name="Apple Inc.", sector="", industry_group=""
        )

        assert request.sector is None
        assert request.industry_group is None

    def test_stock_request_whitespace_only_optional_fields_become_none(self) -> None:
        """Should convert whitespace-only optional fields to None."""
        request = StockRequest(
            symbol="AAPL", name="Apple Inc.", sector="   ", industry_group="   "
        )

        assert request.sector is None
        assert request.industry_group is None

    def test_stock_request_industry_without_sector_raises_validation_error(
        self,
    ) -> None:
        """Should raise ValidationError when industry_group is provided without sector."""
        with pytest.raises(ValidationError) as exc_info:
            _ = StockRequest(
                symbol="AAPL", name="Apple Inc.", industry_group="Software"
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Sector must be provided when industry_group is specified" in str(
            errors[0]["msg"]
        )

    def test_stock_request_to_command_conversion(self) -> None:
        """Should convert to CreateStockCommand correctly."""
        request = StockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Test notes",
        )

        command = request.to_command()

        assert isinstance(command, CreateStockCommand)
        assert command.symbol == "AAPL"
        assert command.name == "Apple Inc."
        assert command.sector == "Technology"
        assert command.industry_group == "Software"
        assert command.grade == "A"
        assert command.notes == "Test notes"

    def test_stock_request_to_command_with_minimal_fields(self) -> None:
        """Should convert minimal request to command correctly."""
        request = StockRequest(symbol="AAPL")

        command = request.to_command()

        assert isinstance(command, CreateStockCommand)
        assert command.symbol == "AAPL"
        assert command.name is None
        assert command.sector is None
        assert command.industry_group is None
        assert command.grade is None
        assert command.notes == ""

    def test_stock_request_json_serialization(self) -> None:
        """Should serialize to JSON correctly."""
        request = StockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            grade="A",
        )

        json_data = request.model_dump()

        expected = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry_group": None,
            "grade": "A",
            "notes": "",
        }
        assert json_data == expected

    def test_stock_request_from_json(self) -> None:
        """Should deserialize from JSON correctly."""
        json_data = {
            "symbol": "aapl",  # lowercase to test normalization
            "name": "  Apple Inc.  ",  # whitespace to test trimming
            "sector": "Technology",
            "grade": "a",  # lowercase to test normalization
        }

        request = StockRequest(**json_data)

        assert request.symbol == "AAPL"
        assert request.name == "Apple Inc."
        assert request.sector == "Technology"
        assert request.grade == "A"

    def test_stock_request_normalize_optional_strings_with_none(self) -> None:
        """Should handle None values correctly in optional field validator."""
        # This test explicitly passes None to ensure coverage of the None check
        request = StockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector=None,  # Explicitly None
            industry_group=None,  # Explicitly None
        )

        assert request.sector is None
        assert request.industry_group is None

    def test_stock_request_normalize_grade_with_none(self) -> None:
        """Should handle None grade correctly in grade validator."""
        # This test explicitly passes None to ensure coverage of the None check
        request = StockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            grade=None,  # Explicitly None
        )

        assert request.grade is None

    def test_stock_request_extra_fields_rejected(self) -> None:
        """Should reject extra fields not in model."""
        with pytest.raises(ValidationError) as exc_info:
            _ = StockRequest(
                symbol="AAPL",
                name="Apple Inc.",
                extra_field="should fail",  # type: ignore[call-arg]
            )

        errors = exc_info.value.errors()
        assert any("extra_field" in str(error) for error in errors)

    def test_stock_request_with_none_name_directly(self) -> None:
        """Should handle None name passed directly."""
        request = StockRequest(symbol="AAPL", name=None)
        assert request.name is None


class TestStockResponse:
    """Test suite for StockResponse model."""

    def test_create_stock_response_with_all_fields(self) -> None:
        """Should create response with all fields."""
        response = StockResponse(
            id="stock-123",
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Excellent company",
        )

        assert response.id == "stock-123"
        assert response.symbol == "AAPL"
        assert response.name == "Apple Inc."
        assert response.sector == "Technology"
        assert response.industry_group == "Software"
        assert response.grade == "A"
        assert response.notes == "Excellent company"

    def test_create_stock_response_with_minimal_fields(self) -> None:
        """Should create response with minimal fields."""
        response = StockResponse(
            id=None,
            symbol="MSFT",
        )

        assert response.id is None
        assert response.symbol == "MSFT"
        assert response.name is None
        assert response.sector is None
        assert response.industry_group is None
        assert response.grade is None
        assert response.notes == ""

    def test_create_stock_response_with_name(self) -> None:
        """Should create response with symbol and name."""
        response = StockResponse(
            id=None,
            symbol="MSFT",
            name="Microsoft Corp.",
        )

        assert response.id is None
        assert response.symbol == "MSFT"
        assert response.name == "Microsoft Corp."
        assert response.sector is None
        assert response.industry_group is None
        assert response.grade is None
        assert response.notes == ""

    def test_stock_response_from_dto_all_fields(self) -> None:
        """Should create from StockDto with all fields."""
        dto = StockDto(
            id="stock-123",
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Test notes",
        )

        response = StockResponse.from_dto(dto)

        assert response.id == "stock-123"
        assert response.symbol == "AAPL"
        assert response.name == "Apple Inc."
        assert response.sector == "Technology"
        assert response.industry_group == "Software"
        assert response.grade == "A"
        assert response.notes == "Test notes"

    def test_stock_response_from_dto_minimal_fields(self) -> None:
        """Should create from StockDto with minimal fields."""
        dto = StockDto(
            id=None,
            symbol="MSFT",
        )

        response = StockResponse.from_dto(dto)

        assert response.id is None
        assert response.symbol == "MSFT"
        assert response.name is None
        assert response.sector is None
        assert response.industry_group is None
        assert response.grade is None
        assert response.notes == ""

    def test_stock_response_json_serialization(self) -> None:
        """Should serialize to JSON correctly."""
        response = StockResponse(
            id="stock-123",
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            grade="A",
            notes="",
        )

        json_data = response.model_dump()

        expected = {
            "id": "stock-123",
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry_group": None,
            "grade": "A",
            "notes": "",
        }
        assert json_data == expected

    def test_stock_response_json_serialization_exclude_none(self) -> None:
        """Should serialize to JSON excluding None values when requested."""
        response = StockResponse(
            id=None,
            symbol="AAPL",
            name="Apple Inc.",
            sector=None,
            industry_group=None,
            grade=None,
            notes="",
        )

        json_data = response.model_dump(exclude_none=True)

        expected = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "notes": "",
        }
        assert json_data == expected

    def test_stock_response_from_json(self) -> None:
        """Should deserialize from JSON correctly."""
        json_data = {
            "id": "stock-123",
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry_group": "Software",
            "grade": "A",
            "notes": "Test notes",
        }

        response = StockResponse(**json_data)

        assert response.id == "stock-123"
        assert response.symbol == "AAPL"
        assert response.name == "Apple Inc."
        assert response.sector == "Technology"
        assert response.industry_group == "Software"
        assert response.grade == "A"
        assert response.notes == "Test notes"

    def test_stock_response_immutability(self) -> None:
        """Response should be immutable after creation."""
        response = StockResponse(
            id="stock-123",
            symbol="AAPL",
            name="Apple Inc.",
        )

        with pytest.raises(ValidationError):
            response.symbol = "MSFT"

    def test_stock_response_model_config(self) -> None:
        """Should have correct model configuration."""
        response = StockResponse(
            id="stock-123",
            symbol="AAPL",
            name="Apple Inc.",
        )

        # Check that model is configured correctly
        assert response.model_config.get("frozen") is True  # Should be immutable

    def test_stock_response_field_validation(self) -> None:
        """Should validate required fields."""
        with pytest.raises(ValidationError) as exc_info:
            _ = StockResponse(
                id="stock-123",
                symbol="",  # Empty symbol should fail
                name="Apple Inc.",
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any("symbol" in str(error) for error in errors)

    def test_stock_response_from_dto_with_different_types(self) -> None:
        """Should handle DTO with consistent types."""
        # Create a DTO with all expected fields
        dto_data: Dict[str, Any] = {
            "id": "stock-123",
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry_group": "Software",
            "grade": "A",
            "notes": "Test notes",
        }

        dto = StockDto(**dto_data)
        response = StockResponse.from_dto(dto)

        assert response.id == dto.id
        assert response.symbol == dto.symbol
        assert response.name == dto.name
        assert response.sector == dto.sector
        assert response.industry_group == dto.industry_group
        assert response.grade == dto.grade
        assert response.notes == dto.notes

    def test_stock_response_validate_name_empty_string(self) -> None:
        """Should handle empty string name validation."""
        response = StockResponse(
            id="stock-123",
            symbol="AAPL",
            name="",  # Empty name should become None
        )
        assert response.name is None


class TestStockModelsIntegration:
    """Integration tests for Stock web models."""

    def test_request_to_command_to_dto_to_response_flow(self) -> None:
        """Should handle full conversion flow correctly."""
        # Start with a request
        request = StockRequest(
            symbol="aapl",  # lowercase to test normalization
            name="  Apple Inc.  ",  # whitespace to test trimming
            sector="Technology",
            industry_group="Software",
            grade="a",  # lowercase to test normalization
            notes="Test notes",
        )

        # Convert to command
        command = request.to_command()
        assert command.symbol == "AAPL"
        assert command.name == "Apple Inc."
        assert command.grade == "A"

        # Simulate creating a DTO from the command (as would happen in app service)
        dto = StockDto(
            id="stock-123",  # ID assigned after creation
            symbol=command.symbol,
            name=command.name,
            sector=command.sector,
            industry_group=command.industry_group,
            grade=command.grade,
            notes=command.notes,
        )

        # Convert DTO to response
        response = StockResponse.from_dto(dto)
        assert response.id == "stock-123"
        assert response.symbol == "AAPL"
        assert response.name == "Apple Inc."
        assert response.sector == "Technology"
        assert response.industry_group == "Software"
        assert response.grade == "A"
        assert response.notes == "Test notes"

    def test_api_json_round_trip(self) -> None:
        """Should handle JSON serialization round trip."""
        # Simulate incoming JSON request
        request_json = {
            "symbol": "msft",
            "name": "Microsoft Corporation",
            "sector": "Technology",
            "grade": "b",
        }

        # Parse request
        request = StockRequest(**request_json)
        assert request.symbol == "MSFT"  # Normalized
        assert request.grade == "B"  # Normalized

        # Convert to command and simulate service processing
        command = request.to_command()

        # Simulate DTO from service
        dto = StockDto(
            id="stock-456",
            symbol=command.symbol,
            name=command.name,
            sector=command.sector,
            industry_group=command.industry_group,
            grade=command.grade,
            notes=command.notes,
        )

        # Create response
        response = StockResponse.from_dto(dto)

        # Serialize response to JSON
        response_json = response.model_dump()

        expected_response = {
            "id": "stock-456",
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "sector": "Technology",
            "industry_group": None,
            "grade": "B",
            "notes": "",
        }
        assert response_json == expected_response

    def test_validation_errors_provide_clear_messages(self) -> None:
        """Should provide clear validation error messages for API consumers."""
        # Test multiple validation errors
        with pytest.raises(ValidationError) as exc_info:
            _ = StockRequest(
                symbol="",  # Empty
                name="",  # Empty
                grade="Z",  # Invalid
                industry_group="Software",  # Without sector
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 2  # At least 2 validation errors

        # Check that error messages are clear
        error_messages = [error["msg"] for error in errors]
        assert any("Symbol cannot be empty" in msg for msg in error_messages)
        # Check for grade validation error instead
        assert any("Grade must be one of" in msg for msg in error_messages)


class TestStockListResponse:
    """Test suite for StockListResponse model."""

    def test_from_dto_list_empty_list(self) -> None:
        """Should handle empty list of DTOs."""
        result = StockListResponse.from_dto_list([])

        assert result.stocks == []
        assert result.total == 0

    def test_from_dto_list_single_dto(self) -> None:
        """Should convert single DTO to list response."""

        dto = StockDto(
            id="stock-123",
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            grade="A",
        )

        result = StockListResponse.from_dto_list([dto])

        assert len(result.stocks) == 1
        assert result.total == 1
        assert result.stocks[0].id == "stock-123"
        assert result.stocks[0].symbol == "AAPL"
        assert result.stocks[0].name == "Apple Inc."

    def test_from_dto_list_multiple_dtos(self) -> None:
        """Should convert multiple DTOs to list response."""

        dtos = [
            StockDto(
                id="stock-123",
                symbol="AAPL",
                name="Apple Inc.",
                sector="Technology",
                grade="A",
            ),
            StockDto(
                id="stock-456",
                symbol="MSFT",
                name="Microsoft Corporation",
                sector="Technology",
                grade="A",
            ),
            StockDto(
                id="stock-789",
                symbol="GOOGL",
                name="Alphabet Inc.",
                sector="Technology",
                grade="B",
            ),
        ]

        result = StockListResponse.from_dto_list(dtos)

        assert len(result.stocks) == 3
        assert result.total == 3

        # Verify all stocks are converted correctly
        symbols = [stock.symbol for stock in result.stocks]
        assert "AAPL" in symbols
        assert "MSFT" in symbols
        assert "GOOGL" in symbols

    def test_from_dto_list_preserves_order(self) -> None:
        """Should preserve the order of DTOs in the response."""

        dtos = [
            StockDto(id="1", symbol="AAPL"),
            StockDto(id="2", symbol="MSFT"),
            StockDto(id="3", symbol="GOOGL"),
        ]

        result = StockListResponse.from_dto_list(dtos)

        assert result.stocks[0].symbol == "AAPL"
        assert result.stocks[1].symbol == "MSFT"
        assert result.stocks[2].symbol == "GOOGL"

    def test_from_dto_list_with_optional_fields(self) -> None:
        """Should handle DTOs with optional fields correctly."""

        dtos = [
            StockDto(
                id=None,  # No ID
                symbol="AAPL",
                name=None,  # No name
                sector=None,  # No sector
                industry_group=None,
                grade=None,
                notes="",
            ),
            StockDto(
                id="stock-123",
                symbol="MSFT",
                name="Microsoft Corporation",
                sector="Technology",
                industry_group="Software",
                grade="A",
                notes="Leading software company",
            ),
        ]

        result = StockListResponse.from_dto_list(dtos)

        assert result.total == 2

        # First stock with minimal fields
        assert result.stocks[0].id is None
        assert result.stocks[0].symbol == "AAPL"
        assert result.stocks[0].name is None
        assert result.stocks[0].sector is None

        # Second stock with all fields
        assert result.stocks[1].id == "stock-123"
        assert result.stocks[1].symbol == "MSFT"
        assert result.stocks[1].name == "Microsoft Corporation"
        assert result.stocks[1].sector == "Technology"

    def test_stock_list_response_immutability(self) -> None:
        """Should be immutable after creation."""

        response = StockListResponse(stocks=[], total=0)

        with pytest.raises(ValidationError):
            response.total = 10

    def test_stock_list_response_json_serialization(self) -> None:
        """Should serialize to JSON correctly."""

        stocks = [
            StockResponse(
                id="stock-123",
                symbol="AAPL",
                name="Apple Inc.",
                sector="Technology",
                grade="A",
            ),
            StockResponse(
                id="stock-456",
                symbol="MSFT",
                name="Microsoft Corporation",
                sector="Technology",
                grade="A",
            ),
        ]

        response = StockListResponse(stocks=stocks, total=2)

        json_data = response.model_dump()

        assert json_data["total"] == 2
        assert len(json_data["stocks"]) == 2
        assert json_data["stocks"][0]["symbol"] == "AAPL"
        assert json_data["stocks"][1]["symbol"] == "MSFT"


class TestStockUpdateRequest:
    """Test suite for StockUpdateRequest validation and behavior."""

    def test_stock_update_request_all_fields(self) -> None:
        """Should accept all valid fields."""
        request = StockUpdateRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Hardware",
            grade="A",
            notes="Updated notes",
        )

        assert request.symbol == "AAPL"
        assert request.name == "Apple Inc."
        assert request.sector == "Technology"
        assert request.industry_group == "Hardware"
        assert request.grade == "A"
        assert request.notes == "Updated notes"

    def test_stock_update_request_partial_fields(self) -> None:
        """Should accept partial updates with only some fields."""
        request = StockUpdateRequest(grade="B", notes="New notes")

        assert request.symbol is None
        assert request.name is None
        assert request.sector is None
        assert request.industry_group is None
        assert request.grade == "B"
        assert request.notes == "New notes"

    def test_stock_update_request_empty_body(self) -> None:
        """Should accept empty request body (all fields None)."""
        request = StockUpdateRequest()

        assert request.symbol is None
        assert request.name is None
        assert request.sector is None
        assert request.industry_group is None
        assert request.grade is None
        assert request.notes == ""  # Notes default to empty string

    def test_stock_update_request_symbol_validation(self) -> None:
        """Should validate symbol format."""
        # Valid symbol
        request = StockUpdateRequest(symbol="AAPL")
        assert request.symbol == "AAPL"

        # Lowercase gets uppercased
        request = StockUpdateRequest(symbol="aapl")
        assert request.symbol == "AAPL"

        # Invalid symbols
        with pytest.raises(ValidationError) as exc_info:
            _ = StockUpdateRequest(symbol="123ABC")
        assert "must contain only uppercase letters" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            _ = StockUpdateRequest(symbol="TOOLONG")
        assert "must be between 1 and 5 characters" in str(exc_info.value)

    def test_stock_update_request_empty_symbol_becomes_none(self) -> None:
        """Should treat empty symbol as None."""
        request = StockUpdateRequest(symbol="")
        assert request.symbol is None

        request = StockUpdateRequest(symbol="   ")
        assert request.symbol is None

    def test_stock_update_request_grade_validation(self) -> None:
        """Should validate grade values."""
        # Valid grades
        for grade in ["A", "B", "C", "D", "F"]:
            request = StockUpdateRequest(grade=grade)
            assert request.grade == grade

        # Lowercase gets uppercased
        request = StockUpdateRequest(grade="a")
        assert request.grade == "A"

        # Invalid grade
        with pytest.raises(ValidationError) as exc_info:
            _ = StockUpdateRequest(grade="Z")
        assert "must be one of A, B, C, D, F" in str(exc_info.value)

        # Empty grade becomes None
        request = StockUpdateRequest(grade="")
        assert request.grade is None

    def test_stock_update_request_whitespace_trimming(self) -> None:
        """Should trim whitespace from all fields."""
        request = StockUpdateRequest(
            symbol="  AAPL  ",
            name="  Apple Inc.  ",
            sector="  Technology  ",
            industry_group="  Hardware  ",
            notes="  Some notes  ",
        )

        assert request.symbol == "AAPL"
        assert request.name == "Apple Inc."
        assert request.sector == "Technology"
        assert request.industry_group == "Hardware"
        assert request.notes == "Some notes"

    def test_stock_update_request_empty_strings_to_none(self) -> None:
        """Should convert empty strings to None for optional fields."""
        request = StockUpdateRequest(name="", sector="", industry_group="", grade="")

        assert request.name is None
        assert request.sector is None
        assert request.industry_group is None
        assert request.grade is None

    def test_stock_update_request_sector_industry_validation(self) -> None:
        """Should validate sector-industry relationship."""
        # Valid combination
        request = StockUpdateRequest(sector="Technology", industry_group="Software")
        assert request.sector == "Technology"
        assert request.industry_group == "Software"

        # Industry without sector should fail
        with pytest.raises(ValidationError) as exc_info:
            _ = StockUpdateRequest(industry_group="Software")
        assert "Sector must be provided when industry_group is specified" in str(
            exc_info.value
        )

    def test_stock_update_request_to_command(self) -> None:
        """Should convert to UpdateStockCommand."""
        request = StockUpdateRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Hardware",
            grade="A",
            notes="Updated",
        )

        command = request.to_command("stock-123")

        assert command.stock_id == "stock-123"
        assert command.symbol == "AAPL"
        assert command.name == "Apple Inc."
        assert command.sector == "Technology"
        assert command.industry_group == "Hardware"
        assert command.grade == "A"
        assert command.notes == "Updated"

    def test_stock_update_request_to_command_with_none_fields(self) -> None:
        """Should handle None fields in to_command."""
        request = StockUpdateRequest()
        command = request.to_command("stock-123")

        assert command.stock_id == "stock-123"
        assert command.symbol is None
        assert command.name is None
        assert command.sector is None
        assert command.industry_group is None
        assert command.grade is None
        assert command.notes == ""

    def test_stock_update_request_extra_fields_rejected(self) -> None:
        """Should reject extra fields not in model."""
        with pytest.raises(ValidationError) as exc_info:
            _ = StockUpdateRequest(symbol="AAPL", unknown_field="value")  # type: ignore[call-arg]
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_stock_request_grade_normalization_empty_string(self) -> None:
        """Should treat empty grade string as None."""
        request = StockRequest(symbol="AAPL", grade="")
        assert request.grade is None

    def test_stock_update_request_symbol_validation_empty_returns_none(self) -> None:
        """Should return None for empty symbol after stripping."""
        request = StockUpdateRequest(symbol="   ")
        assert request.symbol is None

    def test_stock_update_request_name_validation_empty_returns_none(self) -> None:
        """Should return None for empty name after stripping."""
        request = StockUpdateRequest(name="   ")
        assert request.name is None

    def test_stock_update_request_sector_validation_empty_returns_none(self) -> None:
        """Should return None for empty sector after stripping."""
        request = StockUpdateRequest(sector="   ")
        assert request.sector is None

    def test_stock_update_request_grade_normalization_empty_string(self) -> None:
        """Should treat empty grade string as None."""
        request = StockUpdateRequest(grade="")
        assert request.grade is None

    def test_stock_update_request_symbol_validation_none_returns_none(self) -> None:
        """Should return None for None symbol."""
        request = StockUpdateRequest(symbol=None)
        assert request.symbol is None

    def test_stock_update_request_name_validation_none_returns_none(self) -> None:
        """Should return None for None name."""
        request = StockUpdateRequest(name=None)
        assert request.name is None

    def test_stock_update_request_sector_validation_none_returns_none(self) -> None:
        """Should return None for None sector."""
        request = StockUpdateRequest(sector=None)
        assert request.sector is None

    def test_stock_update_request_industry_group_validation_none_returns_none(
        self,
    ) -> None:
        """Should return None for None industry group."""
        request = StockUpdateRequest(industry_group=None)
        assert request.industry_group is None

    def test_stock_update_request_grade_validation_none_returns_none(self) -> None:
        """Should return None for None grade."""
        request = StockUpdateRequest(grade=None)
        assert request.grade is None
