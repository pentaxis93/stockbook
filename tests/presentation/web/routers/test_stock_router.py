"""
Unit tests for stock router.

These tests specifically target the router logic to achieve 100% coverage.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.application.dto.stock_dto import StockDto
from src.application.interfaces.stock_service import IStockApplicationService
from src.domain.exceptions import (
    StockAlreadyExistsError,
    StockNotFoundError,
)
from src.presentation.web.routers import stock_router


class TestStockRouter:
    """Test suite for stock router functionality."""

    @pytest.fixture
    def mock_service(self) -> Mock:
        """Create a mock stock application service."""
        return Mock(spec=IStockApplicationService)

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
        ]

    @pytest.fixture
    def app(self, mock_service: Mock) -> FastAPI:
        """Create FastAPI app with mocked DI container."""
        # Import and register exception handlers
        from src.domain.exceptions import (
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
            not_found_exception_handler,
        )

        # Create a new app instance for each test
        app = FastAPI()
        app.include_router(stock_router.router)

        # Register exception handlers
        app.add_exception_handler(NotFoundError, not_found_exception_handler)
        app.add_exception_handler(AlreadyExistsError, already_exists_exception_handler)
        app.add_exception_handler(
            BusinessRuleViolationError,
            business_rule_violation_exception_handler,
        )
        app.add_exception_handler(DomainError, domain_exception_handler)
        app.add_exception_handler(Exception, generic_exception_handler)

        # Create a mock DI container
        mock_di_container = Mock()
        mock_di_container.resolve.return_value = mock_service

        # Set the DI container in app state
        app.state.di_container = mock_di_container

        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """Create TestClient with exception handling."""
        return TestClient(app, raise_server_exceptions=False)

    def test_get_stock_service_without_di_container_raises_error(self) -> None:
        """Should raise RuntimeError when DI container is not configured."""
        app = FastAPI()
        app.include_router(stock_router.router)

        # Create a mock request without DI container
        mock_request = Mock()
        mock_request.app.state = Mock(spec=[])

        with pytest.raises(RuntimeError) as exc_info:
            _ = stock_router.get_stock_service(mock_request)

        assert str(exc_info.value) == "DI container not configured in app state"

    def test_get_stocks_no_filters_calls_get_all(
        self,
        mock_service: Mock,
        sample_stock_dtos: list[StockDto],
        app: FastAPI,
    ) -> None:
        """Should call get_all_stocks when no filters are provided."""
        mock_service.get_all_stocks.return_value = sample_stock_dtos

        # Set up the service factory
        # Mock service is already set up in the app fixture

        # Create test client with the app that has mocked service
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/stocks")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["stocks"]) == 2

        # Verify get_all_stocks was called
        mock_service.get_all_stocks.assert_called_once()
        mock_service.search_stocks.assert_not_called()

    def test_get_stocks_with_symbol_filter(
        self,
        mock_service: Mock,
        sample_stock_dtos: list[StockDto],
        app: FastAPI,
    ) -> None:
        """Should call search_stocks with symbol filter."""
        filtered_stocks = [sample_stock_dtos[0]]  # Just AAPL
        mock_service.search_stocks.return_value = filtered_stocks

        # Mock service is already set up in the app fixture

        with TestClient(app, raise_server_exceptions=False) as client:
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
        )

    def test_get_stocks_with_multiple_filters(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should call search_stocks with all provided filters."""
        filtered_stock = [
            StockDto(
                id="stock-003",
                symbol="GOOGL",
                name="Alphabet Inc.",
                sector="Technology",
                grade="A",
            ),
        ]
        mock_service.search_stocks.return_value = filtered_stock

        # Mock service is already set up in the app fixture

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get(
                "/stocks",
                params={"symbol": "GOOGL"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

        mock_service.search_stocks.assert_called_once_with(
            symbol_filter="GOOGL",
            name_filter=None,
            industry_filter=None,
        )

    def test_get_stocks_empty_string_filters_ignored(
        self,
        mock_service: Mock,
        sample_stock_dtos: list[StockDto],
        app: FastAPI,
    ) -> None:
        """Should treat empty string filters as None and call get_all_stocks."""
        mock_service.get_all_stocks.return_value = sample_stock_dtos

        # Mock service is already set up in the app fixture

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/stocks", params={"symbol": ""})

        assert response.status_code == 200

        # Should call get_all_stocks since all filters are empty
        mock_service.get_all_stocks.assert_called_once()
        mock_service.search_stocks.assert_not_called()

    def test_get_stocks_whitespace_trimmed_from_filters(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should trim whitespace from filter values."""
        mock_service.search_stocks.return_value = []

        # Mock service is already set up in the app fixture

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get(
                "/stocks",
                params={"symbol": "  AAPL  "},
            )

        assert response.status_code == 200

        # Verify whitespace was trimmed
        mock_service.search_stocks.assert_called_once_with(
            symbol_filter="AAPL",
            name_filter=None,
            industry_filter=None,
        )

    def test_get_stocks_service_exception_returns_500(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should return 500 error when service raises exception."""
        mock_service.get_all_stocks.side_effect = RuntimeError("Database error")

        # Mock service is already set up in the app fixture

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/stocks")

        assert response.status_code == 500
        assert response.json()["detail"] == "An unexpected error occurred"

    def test_get_stocks_service_exception_with_filters(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should handle service exceptions when using filters."""
        mock_service.search_stocks.side_effect = ValueError("Invalid filter")

        # Mock service is already set up in the app fixture

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/stocks", params={"symbol": "INVALID"})

        # ValueError should be converted to 500 error by generic handler
        assert response.status_code == 500
        assert response.json()["detail"] == "An unexpected error occurred"

    def test_get_stocks_response_format(
        self,
        mock_service: Mock,
        sample_stock_dtos: list[StockDto],
        app: FastAPI,
    ) -> None:
        """Should return proper StockListResponse format."""
        mock_service.get_all_stocks.return_value = sample_stock_dtos

        # Mock service is already set up in the app fixture

        with TestClient(app, raise_server_exceptions=False) as client:
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

    def test_get_stocks_empty_result(self, mock_service: Mock, app: FastAPI) -> None:
        """Should handle empty result correctly."""
        mock_service.get_all_stocks.return_value = []

        # Mock service is already set up in the app fixture

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/stocks")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["stocks"] == []

    @patch("src.presentation.web.middleware.exception_handler.logger")
    def test_get_stocks_logs_errors(
        self,
        mock_logger: Mock,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should log errors when exceptions occur."""
        error_msg = "Test error"
        mock_service.get_all_stocks.side_effect = Exception(error_msg)

        # Mock service is already set up in the app fixture

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/stocks")

        assert response.status_code == 500

        # Verify error was logged by the generic exception handler
        mock_logger.exception.assert_called_once()
        log_call = mock_logger.exception.call_args
        # The generic handler logs with format: "Unexpected error at {path}: {error}"
        assert "Unexpected error at" in log_call[0][0]

    def test_update_stock_partial_update_success(
        self,
        mock_service: Mock,
        sample_stock_dtos: list[StockDto],
        app: FastAPI,
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

        mock_service.update_stock.return_value = updated_stock
        # Mock service is already set up in the app fixture

        # App already configured with mock service

        # Act
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(
                f"/stocks/{stock_id}",
                json={"grade": "B", "notes": "Updated notes"},
            )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == stock_id
        assert data["symbol"] == "AAPL"  # Unchanged
        assert data["name"] == "Apple Inc."  # Unchanged
        assert data["grade"] == "B"  # Updated
        assert data["notes"] == "Updated notes"  # Updated

        # Verify service was called with correct command
        mock_service.update_stock.assert_called_once()
        command = mock_service.update_stock.call_args[0][0]
        assert command.stock_id == stock_id
        assert command.grade == "B"
        assert command.notes == "Updated notes"

    def test_update_stock_full_update_success(
        self,
        mock_service: Mock,
        app: FastAPI,
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

        mock_service.update_stock.return_value = updated_stock
        # Mock service is already set up in the app fixture

        # App already configured with mock service

        request_data = {
            "symbol": "APLE",
            "name": "Apple Corporation",
            "sector": "Consumer Electronics",
            "industry_group": "Devices",
            "grade": "C",
            "notes": "Company rebranded",
        }

        # Act
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(f"/stocks/{stock_id}", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == stock_id
        assert data["symbol"] == "APLE"
        assert data["name"] == "Apple Corporation"
        assert data["sector"] == "Consumer Electronics"
        assert data["industry_group"] == "Devices"
        assert data["grade"] == "C"
        assert data["notes"] == "Company rebranded"

        # Verify service was called
        mock_service.update_stock.assert_called_once()

    def test_update_stock_symbol_change(
        self,
        mock_service: Mock,
        sample_stock_dtos: list[StockDto],
        app: FastAPI,
    ) -> None:
        """Should successfully change stock symbol."""
        # Arrange
        stock_id = "stock-001"
        original_stock = sample_stock_dtos[0]

        # Update only the symbol
        updated_stock = StockDto(
            id=original_stock.id,
            symbol="APPL",  # Changed from AAPL
            name=original_stock.name,
            sector=original_stock.sector,
            industry_group=original_stock.industry_group,
            grade=original_stock.grade,
            notes=original_stock.notes,
        )

        mock_service.update_stock.return_value = updated_stock
        # Mock service is already set up in the app fixture

        # App already configured with mock service

        # Act
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(f"/stocks/{stock_id}", json={"symbol": "APPL"})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "APPL"

    def test_update_stock_duplicate_symbol(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should return 409 when changing to an existing symbol."""
        # Arrange
        stock_id = "stock-001"
        mock_service.update_stock.side_effect = StockAlreadyExistsError(
            symbol="MSFT",
        )

        # Mock service is already set up in the app fixture

        # App already configured with mock service

        # Act
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(f"/stocks/{stock_id}", json={"symbol": "MSFT"})

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert "Stock with identifier 'MSFT' already exists" in data["detail"]

    def test_update_stock_not_found(self, mock_service: Mock, app: FastAPI) -> None:
        """Should return 404 when stock doesn't exist."""
        # Arrange
        stock_id = "non-existent-id"
        mock_service.update_stock.side_effect = StockNotFoundError(
            identifier=stock_id,
        )

        # Mock service is already set up in the app fixture

        # App already configured with mock service

        # Act
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(f"/stocks/{stock_id}", json={"grade": "A"})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert f"Stock with identifier '{stock_id}' not found" in data["detail"]

    def test_update_stock_empty_request_body(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should return 200 for empty update request."""
        # Arrange
        stock_id = "stock-001"
        # Empty update is valid - the service should return unchanged stock
        updated_stock = StockDto(
            id=stock_id,
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Hardware",
            grade="A",
            notes="No changes",
        )
        mock_service.update_stock.return_value = updated_stock

        # Mock service is already set up in the app fixture

        # App already configured with mock service

        # Act
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(f"/stocks/{stock_id}", json={})

        # Assert - Empty body is valid in StockUpdateRequest (all fields optional)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == stock_id

    def test_update_stock_invalid_grade(self, app: FastAPI) -> None:
        """Should return 422 for invalid grade values."""
        # Arrange
        stock_id = "stock-001"

        # Mock service is already set up in the app fixture

        # App already configured with mock service

        # Act
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(f"/stocks/{stock_id}", json={"grade": "Z"})

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        # Should be caught by Pydantic validation

    def test_update_stock_invalid_symbol_format(
        self,
        app: FastAPI,
        mock_service: Mock,  # noqa: ARG002
    ) -> None:
        """Should return 422 for invalid symbol format."""
        stock_id = "stock-001"
        test_cases = [
            {"symbol": "123ABC"},  # Numbers
            {"symbol": "AB-CD"},  # Hyphen
            {"symbol": "AB.CD"},  # Dot
            {"symbol": "TOOLONG"},  # Too long
        ]

        # Act & Assert
        with TestClient(app, raise_server_exceptions=False) as client:
            for request_data in test_cases:
                response = client.put(f"/stocks/{stock_id}", json=request_data)
                assert response.status_code == 422
                data = response.json()
                assert "detail" in data
                # Check for Pydantic validation error structure
                assert isinstance(data["detail"], list)
                assert any("symbol" in str(err).lower() for err in data["detail"])

    def test_update_stock_sector_industry_validation(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should validate sector-industry relationship."""
        # Arrange
        stock_id = "stock-001"
        # Use a domain-specific exception instead of ValueError
        from src.domain.exceptions import BusinessRuleViolationError

        mock_service.update_stock.side_effect = BusinessRuleViolationError(
            rule="sector_industry_compatibility",
            context={"sector": "Technology", "industry_group": "Banking"},
        )

        # Mock service is already set up in the app fixture

        # App already configured with mock service

        # Act
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(
                f"/stocks/{stock_id}",
                json={"sector": "Technology", "industry_group": "Banking"},
            )

        # Assert - BusinessRuleViolationError maps to 422 in our handler
        assert response.status_code == 422
        data = response.json()
        assert (
            "Business rule 'sector_industry_compatibility' violated" in data["detail"]
        )

    def test_update_stock_clear_industry_when_sector_changes(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should handle domain logic for sector change clearing industry."""
        # Arrange
        stock_id = "stock-001"

        # The service should handle clearing industry group internally
        updated_stock = StockDto(
            id=stock_id,
            symbol="AAPL",
            name="Apple Inc.",
            sector="Healthcare",  # Changed sector
            industry_group=None,  # Industry cleared
            grade="A",
            notes="Sector change",
        )

        mock_service.update_stock.return_value = updated_stock
        # Mock service is already set up in the app fixture

        # App already configured with mock service

        # Act - only change sector
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(f"/stocks/{stock_id}", json={"sector": "Healthcare"})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["sector"] == "Healthcare"
        assert data["industry_group"] is None

    def test_update_stock_service_error(self, mock_service: Mock, app: FastAPI) -> None:
        """Should return 500 for unexpected service errors."""
        # Arrange
        stock_id = "stock-001"
        mock_service.update_stock.side_effect = Exception("Database error")

        # Mock service is already set up in the app fixture

        # App already configured with mock service

        # Act
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(f"/stocks/{stock_id}", json={"grade": "A"})

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert data["detail"] == "An unexpected error occurred"

    def test_update_stock_whitespace_trimming(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should trim whitespace from all string fields."""
        # Arrange
        stock_id = "stock-001"

        updated_stock = StockDto(
            id=stock_id,
            symbol="TRIM",
            name="Trimmed Company",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Trimmed notes",
        )

        mock_service.update_stock.return_value = updated_stock
        # Mock service is already set up in the app fixture

        # App already configured with mock service

        request_data = {
            "symbol": "  TRIM  ",
            "name": "  Trimmed Company  ",
            "sector": "  Technology  ",
            "industry_group": "  Software  ",
            "notes": "  Trimmed notes  ",
        }

        # Act
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(f"/stocks/{stock_id}", json=request_data)

        # Assert
        assert response.status_code == 200

        # Verify service was called with trimmed values
        mock_service.update_stock.assert_called_once()
        command = mock_service.update_stock.call_args[0][0]
        assert command.symbol == "TRIM"
        assert command.name == "Trimmed Company"
        assert command.sector == "Technology"
        assert command.industry_group == "Software"
        assert command.notes == "Trimmed notes"

    def test_update_stock_empty_strings_as_none(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should treat empty strings as None for optional fields."""
        # Arrange
        stock_id = "stock-001"

        updated_stock = StockDto(
            id=stock_id,
            symbol="EMPT",
            name="Empty Fields Corp.",
            sector=None,
            industry_group=None,
            grade=None,
            notes="",
        )

        mock_service.update_stock.return_value = updated_stock
        # Mock service is already set up in the app fixture

        # App already configured with mock service

        request_data = {
            "name": "Empty Fields Corp.",
            "sector": "",
            "industry_group": "",
            "grade": "",
            "notes": "",
        }

        # Act
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(f"/stocks/{stock_id}", json=request_data)

        # Assert
        assert response.status_code == 200

        # Verify service was called with None for empty fields
        mock_service.update_stock.assert_called_once()
        command = mock_service.update_stock.call_args[0][0]
        assert command.sector is None
        assert command.industry_group is None
        assert command.grade is None
        assert command.notes == ""  # Notes can be empty string

    @patch("src.presentation.web.middleware.exception_handler.logger")
    def test_update_stock_logs_errors(
        self,
        mock_logger: Mock,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should log errors when exceptions occur."""
        # Arrange
        stock_id = "stock-001"
        error_msg = "Test error"
        mock_service.update_stock.side_effect = Exception(error_msg)

        # Mock service is already set up in the app fixture

        # App already configured with mock service

        # Act
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.put(f"/stocks/{stock_id}", json={"grade": "A"})

        # Assert
        assert response.status_code == 500

        # Verify error was logged
        mock_logger.exception.assert_called_once()
        log_args = mock_logger.exception.call_args[0]
        assert "Unexpected error at" in log_args[0]

    def test_create_stock_with_not_found_exception(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should return 404 when create stock raises StockNotFoundError."""
        # This tests the global exception handler for create_stock endpoint
        # Could happen if creating stock references missing entity
        mock_service.create_stock.side_effect = StockNotFoundError(
            identifier="TECH-SECTOR-001",
        )

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post(
                "/stocks",
                json={
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "sector": "Technology",
                },
            )

        assert response.status_code == 404
        data = response.json()
        assert "Stock with identifier 'TECH-SECTOR-001' not found" in data["detail"]

    def test_create_stock_with_already_exists_exception(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Should return 409 when create stock raises StockAlreadyExistsError."""
        # This tests the global exception handler for create_stock endpoint
        mock_service.create_stock.side_effect = StockAlreadyExistsError(
            symbol="AAPL",
        )

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post(
                "/stocks",
                json={
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "sector": "Technology",
                },
            )

        assert response.status_code == 409
        data = response.json()
        assert "Stock with identifier 'AAPL' already exists" in data["detail"]

    def test_get_stock_by_id_endpoint(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Test get_stock_by_id endpoint with domain exceptions."""
        # Test not found
        mock_service.get_stock_by_id.return_value = None

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/stocks/non-existent")

        assert response.status_code == 404
        data = response.json()
        assert "Stock with ID non-existent not found" in data["detail"]

    def test_get_stock_by_id_endpoint_success(
        self,
        mock_service: Mock,
        sample_stock_dtos: list[StockDto],
        app: FastAPI,
    ) -> None:
        """Test get_stock_by_id endpoint success case."""
        stock_dto = sample_stock_dtos[0]
        mock_service.get_stock_by_id.return_value = stock_dto

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get(f"/stocks/{stock_dto.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == stock_dto.id
        assert data["symbol"] == stock_dto.symbol

    def test_get_stock_by_id_endpoint_error(
        self,
        mock_service: Mock,
        app: FastAPI,
    ) -> None:
        """Test get_stock_by_id endpoint with unexpected error."""
        mock_service.get_stock_by_id.side_effect = Exception("Database error")

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/stocks/stock-123")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"] == "An unexpected error occurred"
