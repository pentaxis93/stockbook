"""
Unit tests for stock router.

These tests specifically target the router logic to achieve 100% coverage.
"""

from typing import List
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.application.dto.stock_dto import StockDto
from src.application.services.stock_application_service import StockApplicationService
from src.infrastructure.web.routers import stock_router


class TestStockRouter:
    """Test suite for stock router functionality."""

    @pytest.fixture
    def mock_service(self) -> Mock:
        """Create a mock stock application service."""
        return Mock(spec=StockApplicationService)

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
        ]

    @patch("src.infrastructure.web.routers.stock_router._service_factory", None)
    def test_get_stock_service_without_factory_raises_error(self) -> None:
        """Should raise RuntimeError when service factory is not configured."""
        with pytest.raises(RuntimeError) as exc_info:
            _ = stock_router.get_stock_service()

        assert str(exc_info.value) == "Service factory not configured"

    def test_set_service_factory(self, mock_service: Mock) -> None:
        """Should set the service factory correctly."""

        def factory() -> StockApplicationService:
            return mock_service

        stock_router.set_service_factory(factory)

        # Verify the factory returns our mock
        service = stock_router.get_stock_service()
        assert service is mock_service

    def test_get_stocks_no_filters_calls_get_all(
        self, mock_service: Mock, sample_stock_dtos: List[StockDto]
    ) -> None:
        """Should call get_all_stocks when no filters are provided."""
        mock_service.get_all_stocks.return_value = sample_stock_dtos

        # Set up the service factory
        stock_router.set_service_factory(lambda: mock_service)

        # Create a test client with just the router
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(stock_router.router)

        with TestClient(app) as client:
            response = client.get("/stocks")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["stocks"]) == 2

        # Verify get_all_stocks was called
        mock_service.get_all_stocks.assert_called_once()
        mock_service.search_stocks.assert_not_called()

    def test_get_stocks_with_symbol_filter(
        self, mock_service: Mock, sample_stock_dtos: List[StockDto]
    ) -> None:
        """Should call search_stocks with symbol filter."""
        filtered_stocks = [sample_stock_dtos[0]]  # Just AAPL
        mock_service.search_stocks.return_value = filtered_stocks

        stock_router.set_service_factory(lambda: mock_service)

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(stock_router.router)

        with TestClient(app) as client:
            response = client.get("/stocks", params={"symbol": "AAPL"})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["stocks"][0]["symbol"] == "AAPL"

        # Verify search_stocks was called with correct parameters
        mock_service.search_stocks.assert_called_once_with(
            symbol_filter="AAPL",
            name_filter=None,
            industry_filter=None,
            grade_filter=None,
        )

    def test_get_stocks_with_sector_filter(
        self, mock_service: Mock, sample_stock_dtos: List[StockDto]
    ) -> None:
        """Should call search_stocks with sector filter mapped to industry_filter."""
        mock_service.search_stocks.return_value = sample_stock_dtos

        stock_router.set_service_factory(lambda: mock_service)

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(stock_router.router)

        with TestClient(app) as client:
            response = client.get("/stocks", params={"sector": "Technology"})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

        # Verify sector is mapped to industry_filter
        mock_service.search_stocks.assert_called_once_with(
            symbol_filter=None,
            name_filter=None,
            industry_filter="Technology",  # sector -> industry_filter
            grade_filter=None,
        )

    def test_get_stocks_with_grade_filter(
        self, mock_service: Mock, sample_stock_dtos: List[StockDto]
    ) -> None:
        """Should call search_stocks with grade filter."""
        mock_service.search_stocks.return_value = sample_stock_dtos

        stock_router.set_service_factory(lambda: mock_service)

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(stock_router.router)

        with TestClient(app) as client:
            response = client.get("/stocks", params={"grade": "A"})

        assert response.status_code == 200

        mock_service.search_stocks.assert_called_once_with(
            symbol_filter=None,
            name_filter=None,
            industry_filter=None,
            grade_filter="A",
        )

    def test_get_stocks_with_multiple_filters(self, mock_service: Mock) -> None:
        """Should call search_stocks with all provided filters."""
        filtered_stock = [
            StockDto(
                id="stock-003",
                symbol="GOOGL",
                name="Alphabet Inc.",
                sector="Technology",
                grade="A",
            )
        ]
        mock_service.search_stocks.return_value = filtered_stock

        stock_router.set_service_factory(lambda: mock_service)

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(stock_router.router)

        with TestClient(app) as client:
            response = client.get(
                "/stocks",
                params={"symbol": "GOOGL", "sector": "Technology", "grade": "A"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

        mock_service.search_stocks.assert_called_once_with(
            symbol_filter="GOOGL",
            name_filter=None,
            industry_filter="Technology",
            grade_filter="A",
        )

    def test_get_stocks_empty_string_filters_ignored(
        self, mock_service: Mock, sample_stock_dtos: List[StockDto]
    ) -> None:
        """Should treat empty string filters as None and call get_all_stocks."""
        mock_service.get_all_stocks.return_value = sample_stock_dtos

        stock_router.set_service_factory(lambda: mock_service)

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(stock_router.router)

        with TestClient(app) as client:
            response = client.get(
                "/stocks", params={"symbol": "", "sector": "  ", "grade": ""}
            )

        assert response.status_code == 200

        # Should call get_all_stocks since all filters are empty
        mock_service.get_all_stocks.assert_called_once()
        mock_service.search_stocks.assert_not_called()

    def test_get_stocks_whitespace_trimmed_from_filters(
        self, mock_service: Mock
    ) -> None:
        """Should trim whitespace from filter values."""
        mock_service.search_stocks.return_value = []

        stock_router.set_service_factory(lambda: mock_service)

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(stock_router.router)

        with TestClient(app) as client:
            response = client.get(
                "/stocks",
                params={"symbol": "  AAPL  ", "sector": " Tech ", "grade": " A "},
            )

        assert response.status_code == 200

        # Verify whitespace was trimmed
        mock_service.search_stocks.assert_called_once_with(
            symbol_filter="AAPL",
            name_filter=None,
            industry_filter="Tech",
            grade_filter="A",
        )

    def test_get_stocks_service_exception_returns_500(self, mock_service: Mock) -> None:
        """Should return 500 error when service raises exception."""
        mock_service.get_all_stocks.side_effect = Exception("Database error")

        stock_router.set_service_factory(lambda: mock_service)

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(stock_router.router)

        with TestClient(app) as client:
            response = client.get("/stocks")

        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to retrieve stocks"

    def test_get_stocks_service_exception_with_filters(
        self, mock_service: Mock
    ) -> None:
        """Should handle service exceptions when using filters."""
        mock_service.search_stocks.side_effect = ValueError("Invalid filter")

        stock_router.set_service_factory(lambda: mock_service)

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(stock_router.router)

        with TestClient(app) as client:
            response = client.get("/stocks", params={"symbol": "INVALID"})

        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to retrieve stocks"

    def test_get_stocks_response_format(
        self, mock_service: Mock, sample_stock_dtos: List[StockDto]
    ) -> None:
        """Should return proper StockListResponse format."""
        mock_service.get_all_stocks.return_value = sample_stock_dtos

        stock_router.set_service_factory(lambda: mock_service)

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(stock_router.router)

        with TestClient(app) as client:
            response = client.get("/stocks")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "stocks" in data
        assert "total" in data
        assert isinstance(data["stocks"], list)
        assert isinstance(data["total"], int)

        # Verify stock structure
        for stock in data["stocks"]:
            assert "id" in stock
            assert "symbol" in stock
            assert "name" in stock
            assert "sector" in stock
            assert "industry_group" in stock
            assert "grade" in stock
            assert "notes" in stock

    def test_get_stocks_empty_result(self, mock_service: Mock) -> None:
        """Should handle empty result correctly."""
        mock_service.search_stocks.return_value = []

        stock_router.set_service_factory(lambda: mock_service)

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(stock_router.router)

        with TestClient(app) as client:
            response = client.get("/stocks", params={"grade": "F"})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["stocks"] == []

    @patch("src.infrastructure.web.routers.stock_router.logger")
    def test_get_stocks_logs_errors(
        self, mock_logger: Mock, mock_service: Mock
    ) -> None:
        """Should log errors when exceptions occur."""
        error_msg = "Test error"
        mock_service.get_all_stocks.side_effect = Exception(error_msg)

        stock_router.set_service_factory(lambda: mock_service)

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(stock_router.router)

        with TestClient(app) as client:
            response = client.get("/stocks")

        assert response.status_code == 500

        # Verify error was logged
        mock_logger.error.assert_called_once()
        log_message = mock_logger.error.call_args[0][0]
        assert "Error retrieving stocks:" in log_message
        assert error_msg in log_message
