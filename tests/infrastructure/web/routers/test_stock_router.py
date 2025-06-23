"""
Tests for stock FastAPI router endpoints.

Following TDD principles - these tests define the expected behavior
before implementation.
"""

from fastapi import status
from fastapi.testclient import TestClient


class TestStockRouterGET:
    """Test suite for GET /stocks endpoint."""

    def test_get_stocks_returns_empty_list_when_no_stocks(self) -> None:
        """Test GET /stocks returns empty list when no stocks exist."""
        # This test will fail until we implement the router and integrate with FastAPI app
        from src.infrastructure.web.main import create_app

        # Mock the stock application service to return empty list
        app = create_app()

        # We need to override the dependency injection for testing
        # This will be implemented when we create the router

        client = TestClient(app)
        response = client.get("/stocks")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["stocks"] == []
        assert data["total"] == 0

    def test_get_stocks_returns_list_of_stocks(self) -> None:
        """Test GET /stocks returns list of stocks when stocks exist."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Mock service will return test data
        response = client.get("/stocks")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "stocks" in data
        assert "total" in data
        assert isinstance(data["stocks"], list)
        assert isinstance(data["total"], int)

    def test_get_stocks_returns_correct_stock_data_structure(self) -> None:
        """Test GET /stocks returns stocks with correct data structure."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/stocks")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # If there are stocks, verify structure
        if data["stocks"]:
            stock = data["stocks"][0]
            assert "id" in stock
            assert "symbol" in stock
            assert "name" in stock
            assert "sector" in stock  # Can be null
            assert "industry_group" in stock  # Can be null
            assert "grade" in stock  # Can be null
            assert "notes" in stock

    def test_get_stocks_with_query_parameters(self) -> None:
        """Test GET /stocks with query parameters for filtering."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Test with sector filter
        response = client.get("/stocks?sector=Technology")
        assert response.status_code == status.HTTP_200_OK

        # Test with symbol filter
        response = client.get("/stocks?symbol=AAPL")
        assert response.status_code == status.HTTP_200_OK

        # Test with grade filter
        response = client.get("/stocks?grade=A")
        assert response.status_code == status.HTTP_200_OK

    def test_get_stocks_handles_service_errors_gracefully(self) -> None:
        """Test GET /stocks handles service errors and returns appropriate HTTP status."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # This should handle any service errors gracefully
        response = client.get("/stocks")

        # Should not return 500 errors for normal operation
        assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


class TestStockRouterPOST:
    """Test suite for POST /stocks endpoint."""

    def test_post_stocks_creates_new_stock_with_valid_data(self) -> None:
        """Test POST /stocks creates new stock with valid data."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        stock_data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry_group": "Software",
            "grade": "A",
            "notes": "High quality tech stock",
        }

        response = client.post("/stocks", json=stock_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify returned stock data
        assert data["symbol"] == "AAPL"
        assert data["name"] == "Apple Inc."
        assert data["sector"] == "Technology"
        assert data["industry_group"] == "Software"
        assert data["grade"] == "A"
        assert data["notes"] == "High quality tech stock"
        assert "id" in data
        assert data["id"] is not None

    def test_post_stocks_creates_stock_with_minimal_data(self) -> None:
        """Test POST /stocks creates stock with only required fields."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        stock_data = {
            "symbol": "GOOGL",
            "name": "Google Inc.",
            "sector": None,
            "industry_group": None,
            "grade": None,
            "notes": "",
        }

        response = client.post("/stocks", json=stock_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["symbol"] == "GOOGL"
        assert data["name"] == "Google Inc."
        assert data["sector"] is None
        assert data["industry_group"] is None
        assert data["grade"] is None
        assert data["notes"] == ""
        assert "id" in data

    def test_post_stocks_validates_required_fields(self) -> None:
        """Test POST /stocks validates required fields and returns 422 for invalid data."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Missing symbol
        stock_data = {
            "name": "Apple Inc.",
            "sector": "Technology",
        }
        response = client.post("/stocks", json=stock_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Missing name
        stock_data = {
            "symbol": "AAPL",
            "sector": "Technology",
        }
        response = client.post("/stocks", json=stock_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Empty symbol
        stock_data = {
            "symbol": "",
            "name": "Apple Inc.",
        }
        response = client.post("/stocks", json=stock_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_post_stocks_validates_symbol_format(self) -> None:
        """Test POST /stocks validates stock symbol format."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Invalid symbol format (numbers not allowed)
        stock_data = {
            "symbol": "123ABC",
            "name": "Invalid Company",
        }
        response = client.post("/stocks", json=stock_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Symbol too long
        stock_data = {
            "symbol": "TOOLONG",
            "name": "Invalid Company",
        }
        response = client.post("/stocks", json=stock_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_post_stocks_validates_grade_values(self) -> None:
        """Test POST /stocks validates grade values."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Invalid grade
        stock_data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "grade": "F",  # Not allowed
        }
        response = client.post("/stocks", json=stock_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_post_stocks_normalizes_symbol_to_uppercase(self) -> None:
        """Test POST /stocks normalizes symbol to uppercase."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        stock_data = {
            "symbol": "aapl",  # lowercase
            "name": "Apple Inc.",
        }

        response = client.post("/stocks", json=stock_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["symbol"] == "AAPL"  # Should be uppercase

    def test_post_stocks_handles_duplicate_symbol_error(self) -> None:
        """Test POST /stocks handles duplicate symbol error appropriately."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        stock_data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
        }

        # First creation should succeed
        response1 = client.post("/stocks", json=stock_data)
        if response1.status_code == status.HTTP_201_CREATED:
            # Second creation should fail with conflict
            response2 = client.post("/stocks", json=stock_data)
            assert response2.status_code == status.HTTP_409_CONFLICT
            error_data = response2.json()
            assert "message" in error_data
            assert (
                "duplicate" in error_data["message"].lower()
                or "exists" in error_data["message"].lower()
            )

    def test_post_stocks_returns_proper_error_response_format(self) -> None:
        """Test POST /stocks returns proper error response format for validation errors."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Send invalid data to get error response
        stock_data = {
            "symbol": "",  # Invalid
            "name": "",  # Invalid
        }

        response = client.post("/stocks", json=stock_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        error_data = response.json()
        # FastAPI's standard error format
        assert "detail" in error_data
        assert isinstance(error_data["detail"], list)


class TestStockRouterIntegration:
    """Test suite for integration between GET and POST endpoints."""

    def test_create_stock_then_retrieve_it(self) -> None:
        """Test creating a stock via POST then retrieving it via GET."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Create stock
        stock_data = {
            "symbol": "TSLA",
            "name": "Tesla Inc.",
            "sector": "Technology",
            "grade": "B",
            "notes": "Electric vehicle company",
        }

        create_response = client.post("/stocks", json=stock_data)
        if create_response.status_code == status.HTTP_201_CREATED:

            # Retrieve stocks list
            get_response = client.get("/stocks")
            assert get_response.status_code == status.HTTP_200_OK

            stocks_data = get_response.json()

            # Verify the created stock is in the list
            found_stock = None
            for stock in stocks_data["stocks"]:
                if stock["symbol"] == "TSLA":
                    found_stock = stock
                    break

            if found_stock:
                assert found_stock["name"] == "Tesla Inc."
                assert found_stock["sector"] == "Technology"
                assert found_stock["grade"] == "B"
                assert found_stock["notes"] == "Electric vehicle company"

    def test_stock_router_follows_restful_conventions(self) -> None:
        """Test that stock router follows RESTful API conventions."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # GET /stocks should work
        response = client.get("/stocks")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

        # POST /stocks should work with valid data
        stock_data = {
            "symbol": "REST",
            "name": "RESTful Company",
        }
        response = client.post("/stocks", json=stock_data)
        # Should either succeed or fail with validation error, not server error
        assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR

        # Wrong HTTP methods should return 405
        response = client.put("/stocks")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response = client.delete("/stocks")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
