"""
Integration tests for stock API endpoints.

Following TDD approach - these tests define the expected behavior
of the GET /stocks endpoint before implementation.
"""

from collections.abc import Generator
from unittest.mock import Mock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.application.dto.stock_dto import StockDto
from src.application.services.stock_application_service import StockApplicationService


class TestStockEndpoints:
    """Test suite for stock API endpoints."""

    @pytest.fixture
    def mock_stock_service(self) -> Generator[Mock, None, None]:
        """Mock the stock application service."""
        # Since the endpoint doesn't exist yet, we'll mock at the router level
        mock_instance = Mock(spec=StockApplicationService)
        yield mock_instance

    @pytest.fixture
    def client(self, mock_stock_service: Mock) -> Generator[TestClient, None, None]:
        """Create a test client for the FastAPI app with mocked dependencies."""
        # Import here to ensure clean state for each test
        from src.presentation.web.main import app
        from src.presentation.web.routers import stock_router

        # Override the dependency
        def mock_get_stock_service() -> Mock:
            return mock_stock_service

        app.dependency_overrides[stock_router.get_stock_service] = (
            mock_get_stock_service
        )

        with TestClient(app) as test_client:
            yield test_client

        # Clean up
        app.dependency_overrides.clear()

    @pytest.fixture
    def sample_stock_dtos(self) -> list[StockDto]:
        """Create sample stock DTOs for testing."""
        return [
            StockDto(
                id="stock-001",
                symbol="AAPL",
                name="Apple Inc.",
                sector="Technology",
                industry_group="Hardware",
                grade="A",
                notes="Leading tech company",
            ),
            StockDto(
                id="stock-002",
                symbol="MSFT",
                name="Microsoft Corporation",
                sector="Technology",
                industry_group="Software",
                grade="A",
                notes="Cloud and software giant",
            ),
            StockDto(
                id="stock-003",
                symbol="JPM",
                name="JPMorgan Chase & Co.",
                sector="Financial",
                industry_group="Banking",
                grade="B",
                notes="Major US bank",
            ),
        ]

    def test_get_stocks_empty_list(
        self, client: TestClient, mock_stock_service: Mock
    ) -> None:
        """Should return empty list with total=0 when no stocks exist."""
        # Arrange
        mock_stock_service.get_all_stocks.return_value = []

        # Act
        response = client.get("/stocks")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["stocks"] == []
        assert data["total"] == 0

        # Verify the service was called
        mock_stock_service.get_all_stocks.assert_called_once()

    def test_get_stocks_returns_all_stocks(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: list[StockDto],
    ) -> None:
        """Should return all stocks when multiple exist."""
        # Arrange
        mock_stock_service.get_all_stocks.return_value = sample_stock_dtos

        # Act
        response = client.get("/stocks")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["stocks"]) == 3

        # Verify stock data
        stock_symbols = [stock["symbol"] for stock in data["stocks"]]
        assert "AAPL" in stock_symbols
        assert "MSFT" in stock_symbols
        assert "JPM" in stock_symbols

        # Verify the service was called
        mock_stock_service.get_all_stocks.assert_called_once()

    def test_get_stocks_filter_by_symbol(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: list[StockDto],
    ) -> None:
        """Should filter stocks by symbol (partial match, case-insensitive)."""
        # Arrange
        # Mock the search_stocks method to return filtered results
        filtered_stocks = [stock for stock in sample_stock_dtos if "AP" in stock.symbol]
        mock_stock_service.search_stocks.return_value = filtered_stocks

        # Act
        response = client.get("/stocks", params={"symbol": "ap"})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["stocks"]) == 1
        assert data["stocks"][0]["symbol"] == "AAPL"

        # Verify the service was called with correct filter
        mock_stock_service.search_stocks.assert_called_once_with(
            symbol_filter="ap",
            name_filter=None,
            industry_filter=None,
        )

    def test_get_stocks_no_matches(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: list[StockDto],  # noqa: ARG002
    ) -> None:
        """Should return empty list when no stocks match the filter."""
        # Arrange
        # Return empty list for non-matching filter
        mock_stock_service.search_stocks.return_value = []

        # Act
        response = client.get("/stocks", params={"symbol": "INVALID"})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["stocks"]) == 0

        # Verify the service was called with the filter
        mock_stock_service.search_stocks.assert_called_once_with(
            symbol_filter="INVALID",
            name_filter=None,
            industry_filter=None,
        )

    def test_get_stocks_invalid_query_parameter(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: list[StockDto],
    ) -> None:
        """Should handle invalid/unknown query parameters gracefully."""
        # Arrange
        # Should ignore invalid parameters and return all stocks
        mock_stock_service.get_all_stocks.return_value = sample_stock_dtos

        # Act
        response = client.get(
            "/stocks", params={"invalid_param": "value", "another": "test"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["stocks"]) == 3

        # Verify the service was called to get all stocks (no filters)
        mock_stock_service.get_all_stocks.assert_called_once()

    def test_get_stocks_symbol_filter_case_insensitive(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: list[StockDto],
    ) -> None:
        """Should perform case-insensitive symbol filtering."""
        # Arrange
        apple_stock = [stock for stock in sample_stock_dtos if stock.symbol == "AAPL"]
        mock_stock_service.search_stocks.return_value = apple_stock

        # Act - test with various cases
        test_cases = ["AAPL", "aapl", "AaPl", "aApL"]

        for symbol_case in test_cases:
            response = client.get("/stocks", params={"symbol": symbol_case})

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total"] == 1
            assert data["stocks"][0]["symbol"] == "AAPL"

        # Verify the service was called with the correct number of times
        assert mock_stock_service.search_stocks.call_count == len(test_cases)

    def test_get_stocks_empty_filter_returns_all(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: list[StockDto],
    ) -> None:
        """Should return all stocks when filter values are empty."""
        # Arrange
        mock_stock_service.get_all_stocks.return_value = sample_stock_dtos

        # Act - empty string parameters should be ignored
        response = client.get("/stocks", params={"symbol": "", "sector": ""})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["stocks"]) == 3

        # Verify the service was called to get all stocks (empty filters ignored)
        mock_stock_service.get_all_stocks.assert_called_once()

    def test_get_stocks_response_format(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: list[StockDto],
    ) -> None:
        """Should return response in correct StockListResponse format."""
        # Arrange
        mock_stock_service.get_all_stocks.return_value = sample_stock_dtos

        # Act
        response = client.get("/stocks")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure matches StockListResponse
        assert "stocks" in data
        assert "total" in data
        assert isinstance(data["stocks"], list)
        assert isinstance(data["total"], int)

        # Verify each stock has expected fields
        for stock in data["stocks"]:
            assert "id" in stock
            assert "symbol" in stock
            assert "name" in stock
            assert "sector" in stock
            assert "industry_group" in stock
            assert "grade" in stock
            assert "notes" in stock

    def test_get_stocks_with_all_filters_combined(
        self, client: TestClient, mock_stock_service: Mock
    ) -> None:
        """Should handle all filter parameters combined."""
        # Arrange
        # Create a specific stock that matches all filters
        matching_stock = StockDto(
            id="stock-004",
            symbol="AMZN",
            name="Amazon.com Inc.",
            sector="Technology",
            industry_group="E-Commerce",
            grade="A",
            notes="E-commerce and cloud leader",
        )
        mock_stock_service.search_stocks.return_value = [matching_stock]

        # Act
        response = client.get("/stocks", params={"symbol": "amz"})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["stocks"][0]["symbol"] == "AMZN"

        # Verify the service was called with the symbol filter
        mock_stock_service.search_stocks.assert_called_once_with(
            symbol_filter="amz",
            name_filter=None,
            industry_filter=None,
        )

    def test_get_stock_by_id_success(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: list[StockDto],
    ) -> None:
        """Should retrieve stock by ID successfully."""
        # Arrange
        stock = sample_stock_dtos[0]  # AAPL
        mock_stock_service.get_stock_by_id.return_value = stock

        # Act
        response = client.get(f"/stocks/{stock.id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "stock-001"
        assert data["symbol"] == "AAPL"
        assert data["name"] == "Apple Inc."
        assert data["sector"] == "Technology"
        assert data["industry_group"] == "Hardware"
        assert data["grade"] == "A"
        assert data["notes"] == "Leading tech company"

        # Verify the service was called with correct ID
        mock_stock_service.get_stock_by_id.assert_called_once_with("stock-001")

    def test_get_stock_by_id_not_found(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should return 404 when stock doesn't exist."""
        # Arrange
        stock_id = "non-existent-id"
        mock_stock_service.get_stock_by_id.return_value = None

        # Act
        response = client.get(f"/stocks/{stock_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert f"Stock with ID {stock_id} not found" in data["detail"]

        # Verify the service was called with the ID
        mock_stock_service.get_stock_by_id.assert_called_once_with(stock_id)

    def test_get_stock_by_id_invalid_format(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should handle invalid ID format gracefully."""
        # Arrange
        # Test with various invalid ID formats
        invalid_ids = [
            "",  # Empty ID
            " ",  # Whitespace
            "123 456",  # Space in ID
            "id-with-special-chars!@#",  # Special characters
        ]

        for invalid_id in invalid_ids:
            # For empty or whitespace IDs, FastAPI will interpret as path
            # parameter missing
            # and will return 404 for route not found, not our custom 404
            if invalid_id.strip():
                mock_stock_service.get_stock_by_id.return_value = None

                # Act
                response = client.get(f"/stocks/{invalid_id}")

                # Assert
                # The endpoint should still try to find the stock, even with unusual IDs
                assert response.status_code == status.HTTP_404_NOT_FOUND
                data = response.json()
                assert "detail" in data
                assert (
                    "Stock with ID" in data["detail"] and "not found" in data["detail"]
                )

    def test_get_stock_by_id_service_error(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should handle service errors gracefully."""
        # Arrange
        stock_id = "stock-001"
        mock_stock_service.get_stock_by_id.side_effect = Exception("Database error")

        # Act
        response = client.get(f"/stocks/{stock_id}")

        # Assert
        # The default FastAPI error handler should return 500
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_get_stock_by_id_response_format(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: list[StockDto],
    ) -> None:
        """Should return response in correct StockResponse format."""
        # Arrange
        stock = sample_stock_dtos[1]  # MSFT
        mock_stock_service.get_stock_by_id.return_value = stock

        # Act
        response = client.get(f"/stocks/{stock.id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure matches StockResponse
        expected_fields = [
            "id",
            "symbol",
            "name",
            "sector",
            "industry_group",
            "grade",
            "notes",
        ]
        for field in expected_fields:
            assert field in data
        # Verify data types
        assert isinstance(data["id"], str)
        assert isinstance(data["symbol"], str)
        assert isinstance(data["name"], str)
        assert isinstance(data["sector"], str)
        assert isinstance(data["industry_group"], str)
        assert isinstance(data["grade"], str)
        assert isinstance(data["notes"], str)

    def test_create_stock_with_complete_data(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should create stock successfully with all fields provided."""
        # Arrange
        request_data = {
            "symbol": "GOOGL",
            "name": "Alphabet Inc.",
            "sector": "Technology",
            "industry_group": "Internet Services",
            "grade": "A",
            "notes": "Parent company of Google",
        }

        # Expected response DTO
        created_stock = StockDto(
            id="stock-005",
            symbol="GOOGL",
            name="Alphabet Inc.",
            sector="Technology",
            industry_group="Internet Services",
            grade="A",
            notes="Parent company of Google",
        )
        mock_stock_service.create_stock.return_value = created_stock

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "stock-005"
        assert data["symbol"] == "GOOGL"
        assert data["name"] == "Alphabet Inc."
        assert data["sector"] == "Technology"
        assert data["industry_group"] == "Internet Services"
        assert data["grade"] == "A"
        assert data["notes"] == "Parent company of Google"

        # Verify service was called with correct command
        mock_stock_service.create_stock.assert_called_once()
        command = mock_stock_service.create_stock.call_args[0][0]
        assert command.symbol == "GOOGL"
        assert command.name == "Alphabet Inc."
        assert command.sector == "Technology"
        assert command.industry_group == "Internet Services"
        assert command.grade == "A"
        assert command.notes == "Parent company of Google"

    def test_create_stock_with_minimal_data(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should create stock successfully with only required fields."""
        # Arrange
        request_data = {
            "symbol": "NFLX",
            "name": "Netflix Inc.",
        }

        # Expected response DTO
        created_stock = StockDto(
            id="stock-006",
            symbol="NFLX",
            name="Netflix Inc.",
            sector=None,
            industry_group=None,
            grade=None,
            notes="",
        )
        mock_stock_service.create_stock.return_value = created_stock

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "stock-006"
        assert data["symbol"] == "NFLX"
        assert data["name"] == "Netflix Inc."
        assert data["sector"] is None
        assert data["industry_group"] is None
        assert data["grade"] is None
        assert data["notes"] == ""

        # Verify service was called with correct command
        mock_stock_service.create_stock.assert_called_once()
        command = mock_stock_service.create_stock.call_args[0][0]
        assert command.symbol == "NFLX"
        assert command.name == "Netflix Inc."
        assert command.sector is None
        assert command.industry_group is None
        assert command.grade is None
        assert command.notes == ""

    def test_create_stock_empty_symbol(
        self,
        client: TestClient,
    ) -> None:
        """Should return 422 when symbol is empty."""
        # Arrange
        request_data = {
            "symbol": "",
            "name": "Empty Symbol Corp.",
        }

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        # Pydantic validation should catch this
        assert any("symbol" in str(error.get("loc", [])) for error in data["detail"])

    def test_create_stock_missing_symbol(
        self,
        client: TestClient,
    ) -> None:
        """Should return 422 when symbol is missing."""
        # Arrange
        request_data = {
            "name": "Missing Symbol Corp.",
        }

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_create_stock_invalid_symbol_format(
        self,
        client: TestClient,
    ) -> None:
        """Should return 422 when symbol contains non-alphabetic characters."""
        # Arrange
        test_cases = [
            {"symbol": "123ABC", "name": "Invalid Symbol 1"},
            {"symbol": "AB-CD", "name": "Invalid Symbol 2"},
            {"symbol": "AB.CD", "name": "Invalid Symbol 3"},
            {"symbol": "AB CD", "name": "Invalid Symbol 4"},
        ]

        for request_data in test_cases:
            # Act
            response = client.post("/stocks", json=request_data)

            # Assert
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            data = response.json()
            assert "detail" in data

    def test_create_stock_symbol_too_long(
        self,
        client: TestClient,
    ) -> None:
        """Should return 422 when symbol exceeds 5 characters."""
        # Arrange
        request_data = {
            "symbol": "TOOLONG",
            "name": "Too Long Symbol Corp.",
        }

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_create_stock_empty_name(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should return 422 when name is empty."""
        # Arrange
        request_data = {
            "symbol": "EMPT",
            "name": "",
        }

        # Mock service to raise ValueError (domain validation)
        mock_stock_service.create_stock.side_effect = ValueError(
            "Company name cannot be empty"
        )

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        assert "Company name cannot be empty" in data["detail"]

    def test_create_stock_missing_name(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should return 422 when name is missing."""
        # Arrange
        request_data = {
            "symbol": "MISS",
        }

        # Mock service to raise ValueError (domain validation)
        mock_stock_service.create_stock.side_effect = ValueError(
            "Company name is required"
        )

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        assert "Company name is required" in data["detail"]

    def test_create_stock_name_too_long(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should return 422 when name exceeds 200 characters."""
        # Arrange
        long_name = "A" * 201
        request_data = {
            "symbol": "LONG",
            "name": long_name,
        }

        # Mock service to raise ValueError (domain validation)
        mock_stock_service.create_stock.side_effect = ValueError(
            "Company name cannot exceed 200 characters"
        )

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        assert "Company name cannot exceed 200 characters" in data["detail"]

    def test_create_stock_invalid_grade(
        self,
        client: TestClient,
    ) -> None:
        """Should return 422 when grade is not A, B, C, D, or F."""
        # Arrange
        request_data = {
            "symbol": "INVG",
            "name": "Invalid Grade Corp.",
            "grade": "Z",
        }

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_create_stock_duplicate(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should return 400 when stock with symbol already exists."""
        # Arrange
        request_data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
        }

        # Mock service to raise ValueError for duplicate
        mock_stock_service.create_stock.side_effect = ValueError(
            "Stock with symbol AAPL already exists"
        )

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"]

    def test_create_stock_symbol_sanitization(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should uppercase symbol and trim whitespace."""
        # Arrange
        request_data = {
            "symbol": "  aapl  ",
            "name": "Apple Inc.",
        }

        # Expected response DTO
        created_stock = StockDto(
            id="stock-007",
            symbol="AAPL",
            name="Apple Inc.",
            sector=None,
            industry_group=None,
            grade=None,
            notes="",
        )
        mock_stock_service.create_stock.return_value = created_stock

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["symbol"] == "AAPL"

        # Verify service was called with normalized symbol
        mock_stock_service.create_stock.assert_called_once()
        command = mock_stock_service.create_stock.call_args[0][0]
        assert command.symbol == "AAPL"

    def test_create_stock_whitespace_trimming(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should trim whitespace from all string fields."""
        # Arrange
        request_data = {
            "symbol": "  TRIM  ",
            "name": "  Trimmed Company  ",
            "sector": "  Technology  ",
            "industry_group": "  Software  ",
            "notes": "  Some notes  ",
        }

        # Expected response DTO
        created_stock = StockDto(
            id="stock-008",
            symbol="TRIM",
            name="Trimmed Company",
            sector="Technology",
            industry_group="Software",
            grade=None,
            notes="Some notes",
        )
        mock_stock_service.create_stock.return_value = created_stock

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED

        # Verify service was called with trimmed values
        mock_stock_service.create_stock.assert_called_once()
        command = mock_stock_service.create_stock.call_args[0][0]
        assert command.symbol == "TRIM"
        assert command.name == "Trimmed Company"
        assert command.sector == "Technology"
        assert command.industry_group == "Software"
        assert command.notes == "Some notes"

    def test_create_stock_empty_strings_as_none(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should treat empty strings as None for optional fields."""
        # Arrange
        request_data = {
            "symbol": "EMPT",
            "name": "Empty Fields Corp.",
            "sector": "",
            "industry_group": "",
            "grade": "",
            "notes": "",
        }

        # Expected response DTO
        created_stock = StockDto(
            id="stock-009",
            symbol="EMPT",
            name="Empty Fields Corp.",
            sector=None,
            industry_group=None,
            grade=None,
            notes="",
        )
        mock_stock_service.create_stock.return_value = created_stock

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED

        # Verify service was called with None for empty optional fields
        mock_stock_service.create_stock.assert_called_once()
        command = mock_stock_service.create_stock.call_args[0][0]
        assert command.sector is None
        assert command.industry_group is None
        assert command.grade is None
        assert command.notes == ""  # Notes can be empty string

    def test_create_stock_service_error(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should return 500 when service raises unexpected error."""
        # Arrange
        request_data = {
            "symbol": "ERR",
            "name": "Error Corp.",
        }

        # Mock service to raise unexpected error
        mock_stock_service.create_stock.side_effect = RuntimeError(
            "Database connection failed"
        )

        # Act
        response = client.post("/stocks", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Failed to create stock"
        # Should not expose internal error details
        assert "Database connection failed" not in data["detail"]

    def test_update_stock_partial_update_success(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: list[StockDto],
    ) -> None:
        """Should successfully update only specified fields."""
        # Arrange
        stock_id = "stock-001"
        original_stock = sample_stock_dtos[0]  # AAPL

        # Create an updated version with only grade and notes changed
        updated_stock = StockDto(
            id=original_stock.id,
            symbol=original_stock.symbol,
            name=original_stock.name,
            sector=original_stock.sector,
            industry_group=original_stock.industry_group,
            grade="B",  # Changed from A
            notes="Updated notes",  # Changed
        )

        mock_stock_service.update_stock.return_value = updated_stock

        # Act
        response = client.put(
            f"/stocks/{stock_id}", json={"grade": "B", "notes": "Updated notes"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == stock_id
        assert data["symbol"] == "AAPL"  # Unchanged
        assert data["name"] == "Apple Inc."  # Unchanged
        assert data["grade"] == "B"  # Updated
        assert data["notes"] == "Updated notes"  # Updated

        # Verify service was called with correct command
        mock_stock_service.update_stock.assert_called_once()
        command = mock_stock_service.update_stock.call_args[0][0]
        assert command.stock_id == stock_id
        assert command.grade == "B"
        assert command.notes == "Updated notes"

    def test_update_stock_full_update_success(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should successfully update all updatable fields including symbol."""
        # Arrange
        stock_id = "stock-001"

        # Create an updated stock with all fields changed
        updated_stock = StockDto(
            id=stock_id,
            symbol="APLE",  # Changed symbol
            name="Apple Corporation",  # Changed name
            sector="Consumer Electronics",  # Changed sector
            industry_group="Devices",  # Changed industry group
            grade="C",  # Changed grade
            notes="Company rebranded",  # Changed notes
        )

        mock_stock_service.update_stock.return_value = updated_stock

        request_data = {
            "symbol": "APLE",
            "name": "Apple Corporation",
            "sector": "Consumer Electronics",
            "industry_group": "Devices",
            "grade": "C",
            "notes": "Company rebranded",
        }

        # Act
        response = client.put(f"/stocks/{stock_id}", json=request_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == stock_id
        assert data["symbol"] == "APLE"
        assert data["name"] == "Apple Corporation"
        assert data["sector"] == "Consumer Electronics"
        assert data["industry_group"] == "Devices"
        assert data["grade"] == "C"
        assert data["notes"] == "Company rebranded"

    def test_update_stock_not_found(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should return 404 when stock doesn't exist."""
        # Arrange
        stock_id = "non-existent-id"
        mock_stock_service.update_stock.side_effect = ValueError(
            f"Stock with ID {stock_id} not found"
        )

        # Act
        response = client.put(f"/stocks/{stock_id}", json={"grade": "A"})

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_update_stock_duplicate_symbol(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should return 400 when changing to an existing symbol."""
        # Arrange
        stock_id = "stock-001"
        mock_stock_service.update_stock.side_effect = ValueError(
            "Stock with symbol MSFT already exists"
        )

        # Act
        response = client.put(f"/stocks/{stock_id}", json={"symbol": "MSFT"})

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "already exists" in data["detail"]

    def test_update_stock_invalid_grade(
        self,
        client: TestClient,
    ) -> None:
        """Should return 422 for invalid grade values."""
        # Arrange
        stock_id = "stock-001"

        # Act
        response = client.put(f"/stocks/{stock_id}", json={"grade": "Z"})

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_update_stock_empty_request_body(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should return 422 for empty update request."""
        # Arrange
        stock_id = "stock-001"
        mock_stock_service.update_stock.side_effect = ValueError("No fields to update")

        # Act
        response = client.put(f"/stocks/{stock_id}", json={})

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "No fields to update" in data["detail"]

    def test_update_stock_symbol_validation(
        self,
        client: TestClient,
    ) -> None:
        """Should validate symbol format."""
        # Arrange
        stock_id = "stock-001"

        test_cases = [
            {"symbol": "123ABC"},  # Numbers
            {"symbol": "AB-CD"},  # Hyphen
            {"symbol": "TOOLONG"},  # Too long
        ]

        # Act & Assert
        for request_data in test_cases:
            response = client.put(f"/stocks/{stock_id}", json=request_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_stock_service_error(
        self,
        client: TestClient,
        mock_stock_service: Mock,
    ) -> None:
        """Should return 500 for unexpected service errors."""
        # Arrange
        stock_id = "stock-001"
        mock_stock_service.update_stock.side_effect = RuntimeError("Database error")

        # Act
        response = client.put(f"/stocks/{stock_id}", json={"grade": "A"})

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["detail"] == "Failed to update stock"
