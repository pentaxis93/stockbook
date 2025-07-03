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
            grade_filter=None,
        )

    def test_get_stocks_filter_by_sector(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: List[StockDto],
    ) -> None:
        """Should filter stocks by sector."""
        # Arrange
        tech_stocks = [
            stock for stock in sample_stock_dtos if stock.sector == "Technology"
        ]
        mock_stock_service.search_stocks.return_value = tech_stocks

        # Act
        response = client.get("/stocks", params={"sector": "Technology"})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["stocks"]) == 2

        # Verify all returned stocks are in Technology sector
        for stock in data["stocks"]:
            assert stock["sector"] == "Technology"

        # Note: The service expects sector filter as industry_filter parameter
        mock_stock_service.search_stocks.assert_called_once_with(
            symbol_filter=None,
            name_filter=None,
            industry_filter="Technology",
            grade_filter=None,
        )

    def test_get_stocks_filter_by_grade(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: List[StockDto],
    ) -> None:
        """Should filter stocks by grade."""
        # Arrange
        grade_a_stocks = [stock for stock in sample_stock_dtos if stock.grade == "A"]
        mock_stock_service.search_stocks.return_value = grade_a_stocks

        # Act
        response = client.get("/stocks", params={"grade": "A"})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["stocks"]) == 2

        # Verify all returned stocks have grade A
        for stock in data["stocks"]:
            assert stock["grade"] == "A"

        # Verify the service was called with correct filter
        mock_stock_service.search_stocks.assert_called_once_with(
            symbol_filter=None,
            name_filter=None,
            industry_filter=None,
            grade_filter="A",
        )

    def test_get_stocks_combine_multiple_filters(
        self,
        client: TestClient,
        mock_stock_service: Mock,
        sample_stock_dtos: List[StockDto],
    ) -> None:
        """Should apply multiple filters simultaneously."""
        # Arrange
        # Filter for Technology sector with grade A
        filtered_stocks = [
            stock
            for stock in sample_stock_dtos
            if stock.sector == "Technology" and stock.grade == "A"
        ]
        mock_stock_service.search_stocks.return_value = filtered_stocks

        # Act
        response = client.get("/stocks", params={"sector": "Technology", "grade": "A"})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["stocks"]) == 2

        # Verify all returned stocks match both criteria
        for stock in data["stocks"]:
            assert stock["sector"] == "Technology"
            assert stock["grade"] == "A"

        # Verify the service was called with multiple filters
        mock_stock_service.search_stocks.assert_called_once_with(
            symbol_filter=None,
            name_filter=None,
            industry_filter="Technology",
            grade_filter="A",
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
        response = client.get(
            "/stocks", params={"symbol": "", "sector": "", "grade": ""}
        )

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
        response = client.get(
            "/stocks", params={"symbol": "amz", "sector": "Technology", "grade": "A"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["stocks"][0]["symbol"] == "AMZN"

        # Verify the service was called with all filters
        mock_stock_service.search_stocks.assert_called_once_with(
            symbol_filter="amz",
            name_filter=None,
            industry_filter="Technology",
            grade_filter="A",
        )
