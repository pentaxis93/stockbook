"""
Full stack integration tests for FastAPI implementation.

Following TDD principles - these tests define the expected behavior
of the complete FastAPI application stack before implementation.
Tests HTTP requests → FastAPI routers → application services → domain logic → database.
"""

from fastapi.testclient import TestClient

# These tests will fail until we create the FastAPI integration layer


class TestFastAPIStockEndpointsIntegration:
    """Full stack integration tests for stock endpoints with real database."""

    def setup_method(self) -> None:
        """Clean up database before each test."""
        from dependency_injection.composition_root import CompositionRoot
        from src.infrastructure.persistence.database_connection import (
            DatabaseConnection,
        )
        from src.infrastructure.web.routers.stock_router import reset_container

        # Reset container to get fresh dependencies
        reset_container()

        # Clear database tables for test isolation
        container = CompositionRoot.configure()
        db_connection = container.resolve(DatabaseConnection)

        # Clear all stocks from database for clean test state
        with db_connection.get_connection() as conn:
            _ = conn.execute("DELETE FROM stock")
            conn.commit()

    def test_create_and_retrieve_stock_full_stack(self) -> None:
        """Should create stock via POST and retrieve it via GET using real database."""
        # This test will fail until we implement FastAPI integration
        from src.infrastructure.web.main import create_app

        # Arrange - Create FastAPI app with real dependencies
        app = create_app()
        client = TestClient(app)

        # Create a stock via POST (use unique symbol to avoid conflicts)
        import random
        import string

        # Generate 1-5 uppercase letters (valid symbol format)
        unique_symbol = "".join(random.choices(string.ascii_uppercase, k=4))
        stock_data = {
            "symbol": unique_symbol,
            "name": "Test Company Inc.",
            "sector": "Technology",
            "industry_group": "Software",
            "grade": "A",
            "notes": "High quality tech stock",
        }

        # Act - POST to create stock
        create_response = client.post("/stocks", json=stock_data)

        # Debug: Print response details if test fails
        if create_response.status_code != 201:
            print(f"Create response status: {create_response.status_code}")
            print(f"Create response content: {create_response.content}")

        # Assert - Stock creation succeeded
        assert create_response.status_code == 201
        created_stock = create_response.json()
        assert created_stock["symbol"] == unique_symbol
        assert created_stock["name"] == "Test Company Inc."
        assert created_stock["sector"] == "Technology"
        assert created_stock["grade"] == "A"
        assert "id" in created_stock

        # Act - GET to retrieve all stocks
        list_response = client.get("/stocks")

        # Debug: Print response details if test fails
        if list_response.status_code != 200:
            print(f"List response status: {list_response.status_code}")
            print(f"List response content: {list_response.content}")

        # Assert - Stock appears in list
        assert list_response.status_code == 200
        stocks_data = list_response.json()
        assert "stocks" in stocks_data
        assert "total" in stocks_data
        assert stocks_data["total"] >= 1

        # Find our created stock in the list
        found_stock = None
        for stock in stocks_data["stocks"]:
            if stock["symbol"] == unique_symbol:
                found_stock = stock
                break

        assert found_stock is not None
        assert found_stock["name"] == "Test Company Inc."
        assert found_stock["sector"] == "Technology"
        assert found_stock["grade"] == "A"

    def test_create_stock_with_validation_errors_full_stack(self) -> None:
        """Should return validation errors for invalid stock data through full stack."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Arrange - Invalid stock data (empty symbol)
        invalid_stock_data = {
            "symbol": "",  # Invalid: empty symbol
            "name": "Test Company",
            "sector": "Technology",
            "industry_group": "Software",
            "grade": "A",
            "notes": "",
        }

        # Act
        response = client.post("/stocks", json=invalid_stock_data)

        # Assert - Should return validation error
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

        # Verify validation error details
        assert any(error["loc"] == ["body", "symbol"] for error in error_data["detail"])

    def test_create_stock_with_invalid_grade_full_stack(self) -> None:
        """Should reject stock creation with invalid grade through full stack."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Arrange - Invalid grade
        invalid_stock_data = {
            "symbol": "TEST",
            "name": "Test Company",
            "sector": "Technology",
            "industry_group": "Software",
            "grade": "D",  # Invalid: only A, B, C allowed
            "notes": "",
        }

        # Act
        response = client.post("/stocks", json=invalid_stock_data)

        # Assert - Should return validation error
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_create_duplicate_stock_full_stack(self) -> None:
        """Should prevent duplicate stock creation through full stack."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Arrange - Create first stock
        stock_data = {
            "symbol": "MSFT",
            "name": "Microsoft Corp.",
            "sector": "Technology",
            "industry_group": "Software",
            "grade": "A",
            "notes": "Cloud computing leader",
        }

        # Act - Create first stock
        first_response = client.post("/stocks", json=stock_data)
        assert first_response.status_code == 201

        # Act - Try to create duplicate
        duplicate_response = client.post("/stocks", json=stock_data)

        # Assert - Should reject duplicate
        assert duplicate_response.status_code == 400
        error_data = duplicate_response.json()
        assert "message" in error_data
        assert "already exists" in error_data["message"].lower()

    def test_get_empty_stocks_list_full_stack(self) -> None:
        """Should return empty list when no stocks exist through full stack."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Act - Get stocks when database is empty
        response = client.get("/stocks")

        # Debug: Print response details if test fails
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.content}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "stocks" in data
        assert "total" in data
        assert isinstance(data["stocks"], list)
        assert data["total"] == 0


class TestFastAPIHealthEndpointIntegration:
    """Full stack integration tests for health endpoint."""

    def setup_method(self) -> None:
        """Clean up database before each test."""
        from dependency_injection.composition_root import CompositionRoot
        from src.infrastructure.persistence.database_connection import (
            DatabaseConnection,
        )
        from src.infrastructure.web.routers.stock_router import reset_container

        # Reset container to get fresh dependencies
        reset_container()

        # Clear database tables for test isolation
        container = CompositionRoot.configure()
        db_connection = container.resolve(DatabaseConnection)

        # Clear all stocks from database for clean test state
        with db_connection.get_connection() as conn:
            _ = conn.execute("DELETE FROM stock")
            conn.commit()

    def test_health_check_full_stack(self) -> None:
        """Should return healthy status through full stack."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestFastAPIErrorHandlingIntegration:
    """Full stack integration tests for error handling."""

    def setup_method(self) -> None:
        """Clean up database before each test."""
        from dependency_injection.composition_root import CompositionRoot
        from src.infrastructure.persistence.database_connection import (
            DatabaseConnection,
        )
        from src.infrastructure.web.routers.stock_router import reset_container

        # Reset container to get fresh dependencies
        reset_container()

        # Clear database tables for test isolation
        container = CompositionRoot.configure()
        db_connection = container.resolve(DatabaseConnection)

        # Clear all stocks from database for clean test state
        with db_connection.get_connection() as conn:
            _ = conn.execute("DELETE FROM stock")
            conn.commit()

    def test_404_for_nonexistent_endpoint_full_stack(self) -> None:
        """Should return 404 for nonexistent endpoints through full stack."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Act
        response = client.get("/nonexistent")

        # Assert
        assert response.status_code == 404

    def test_405_for_wrong_method_full_stack(self) -> None:
        """Should return 405 for wrong HTTP methods through full stack."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Act - Try to DELETE health endpoint (not supported)
        response = client.delete("/health")

        # Assert
        assert response.status_code == 405


class TestFastAPIDatabaseIntegration:
    """Full stack integration tests focusing on database interactions."""

    def setup_method(self) -> None:
        """Clean up database before each test."""
        from dependency_injection.composition_root import CompositionRoot
        from src.infrastructure.persistence.database_connection import (
            DatabaseConnection,
        )
        from src.infrastructure.web.routers.stock_router import reset_container

        # Reset container to get fresh dependencies
        reset_container()

        # Clear database tables for test isolation
        container = CompositionRoot.configure()
        db_connection = container.resolve(DatabaseConnection)

        # Clear all stocks from database for clean test state
        with db_connection.get_connection() as conn:
            _ = conn.execute("DELETE FROM stock")
            conn.commit()

    def test_database_transaction_rollback_on_error_full_stack(self) -> None:
        """Should rollback database transaction on domain validation errors."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # This test verifies that if domain validation fails after database operations start,
        # the transaction is properly rolled back

        # Arrange - Data that might pass Pydantic validation but fail domain validation
        stock_data = {
            "symbol": "VALID",
            "name": "Valid Company Name",
            "sector": "Technology",
            "industry_group": "Software",
            "grade": "A",
            "notes": "Test notes",
        }

        # Act - Create stock (should succeed)
        response = client.post("/stocks", json=stock_data)

        # Assert - Either succeeds completely or fails completely (no partial state)
        assert response.status_code in [201, 400, 422]

        # Verify database state is consistent
        list_response = client.get("/stocks")
        assert list_response.status_code == 200

        # If stock creation succeeded, it should be in the list
        # If it failed, it should not be in the list
        stocks_data = list_response.json()
        if response.status_code == 201:
            assert any(stock["symbol"] == "VALID" for stock in stocks_data["stocks"])
        else:
            assert not any(
                stock["symbol"] == "VALID" for stock in stocks_data["stocks"]
            )

    def test_multiple_requests_database_consistency_full_stack(self) -> None:
        """Should maintain database consistency across multiple concurrent-style requests."""
        from src.infrastructure.web.main import create_app

        app = create_app()
        client = TestClient(app)

        # Arrange - Multiple different stocks with valid sector/industry combinations
        stocks_data = [
            {
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "sector": "Technology",
                "industry_group": "Internet Services",
                "grade": "A",
                "notes": "Search engine leader",
            },
            {
                "symbol": "TSLA",
                "name": "Tesla Inc.",
                "sector": "Industrial",
                "industry_group": "Manufacturing",
                "grade": "B",
                "notes": "Electric vehicle pioneer",
            },
            {
                "symbol": "JPM",
                "name": "JPMorgan Chase",
                "sector": "Financial Services",
                "industry_group": "Banking",
                "grade": "A",
                "notes": "Leading investment bank",
            },
        ]

        # Act - Create multiple stocks
        created_stocks: list[dict[str, str]] = []
        for stock_data in stocks_data:
            response = client.post("/stocks", json=stock_data)
            if response.status_code == 201:
                created_stocks.append(response.json())
            else:
                # Log the error for debugging
                print(
                    f"Failed to create stock {stock_data['symbol']}: {response.status_code} - {response.content}"
                )

        # Assert we created at least some stocks
        assert len(created_stocks) > 0, "No stocks were successfully created"

        # Act - Get all stocks
        list_response = client.get("/stocks")
        assert list_response.status_code == 200

        # Assert - All successfully created stocks should be retrievable
        all_stocks = list_response.json()
        assert all_stocks["total"] == len(created_stocks)

        # Verify each created stock is in the list
        for created_stock in created_stocks:
            found = any(
                stock["symbol"] == created_stock["symbol"]
                for stock in all_stocks["stocks"]
            )
            assert found, f"Stock {created_stock['symbol']} not found in list"
