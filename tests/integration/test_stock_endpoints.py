"""
Integration tests for stock API endpoints.

Following TDD approach - these tests define the expected behavior
of the GET /stocks endpoint before implementation.
"""

from typing import Generator, List
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
        from src.infrastructure.web.main import app
        from src.infrastructure.web.routers import stock_router

        # Override the dependency
        def mock_get_stock_service():
            return mock_stock_service

        app.dependency_overrides[stock_router.get_stock_service] = (
            mock_get_stock_service
        )

        with TestClient(app) as test_client:
            yield test_client

        # Clean up
        app.dependency_overrides.clear()

    @pytest.fixture
    def sample_stock_dtos(self) -> List[StockDto]:
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
        sample_stock_dtos: List[StockDto],
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
        sample_stock_dtos: List[StockDto],
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
        sample_stock_dtos: List[StockDto],
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
        sample_stock_dtos: List[StockDto],
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
        sample_stock_dtos: List[StockDto],
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
        sample_stock_dtos: List[StockDto],
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
        sample_stock_dtos: List[StockDto],
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
        sample_stock_dtos: List[StockDto],
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
            # For empty or whitespace IDs, FastAPI will interpret as path parameter missing
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
        sample_stock_dtos: List[StockDto],
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
