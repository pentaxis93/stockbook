"""Tests for the main FastAPI application."""

import os
import re
from collections.abc import Iterator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient


class TestMainApp:
    """Test suite for the main FastAPI application."""

    @pytest.fixture
    def mock_database_initializer(self) -> Iterator[Mock]:
        """Mock the database initializer to avoid actual database operations."""
        with patch("src.presentation.web.main.initialize_database") as mock:
            yield mock

    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client for the FastAPI app."""
        # Import here to ensure mocks are in place
        from src.presentation.web.main import app

        return TestClient(app)

    def test_app_creation(self, client: TestClient) -> None:
        """Test that the FastAPI app is created successfully."""
        assert client.app is not None
        # Check app info via the API endpoint instead of attributes
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "StockBook API"
        # Just verify version exists, don't hardcode the value
        assert "version" in data
        assert isinstance(data["version"], str)

    def test_database_initialization_on_startup(
        self,
        mock_database_initializer: Mock,
    ) -> None:
        """Test that database is initialized during app startup."""
        # Import and trigger startup by creating the app
        from src.presentation.web.main import app

        # Manually trigger startup event
        with TestClient(app):
            # Verify database initializer was called with correct path
            mock_database_initializer.assert_called_once()

            # Get the actual call arguments
            call_args = mock_database_initializer.call_args[0]
            assert len(call_args) == 1

            # Should be called with the database URL from environment or config
            from config import Config

            config = Config()
            expected_url = os.getenv("DATABASE_URL", config.database_url)
            assert call_args[0] == expected_url

    def test_health_check_endpoint(self, client: TestClient) -> None:
        """Test the health check endpoint returns successful response."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "StockBook API"}

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test the root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "StockBook API"
        # Version should exist and follow semantic versioning format
        assert "version" in data
        assert isinstance(data["version"], str)
        # Should match X.Y.Z format
        import re

        assert re.match(r"^\d+\.\d+\.\d+$", data["version"])
        assert "endpoints" in data
        assert "/health" in data["endpoints"]
        assert "/docs" in data["endpoints"]

    def test_version_endpoint(self, client: TestClient) -> None:
        """Test version endpoint returns correct version information."""
        response = client.get("/version")
        assert response.status_code == 200

        data = response.json()
        # Verify version exists and has expected format
        assert "version" in data
        assert isinstance(data["version"], str)
        assert re.match(r"^\d+\.\d+\.\d+$", data["version"])
        # Verify release date exists and has expected format
        assert "release_date" in data
        assert isinstance(data["release_date"], str)
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", data["release_date"])
        assert data["api_version"] == "v1"
        assert "name" in data
        assert data["name"] == "StockBook"

    def test_database_initialization_error_handling(self) -> None:
        """Test that database initialization errors are logged but don't crash
        the app."""
        with patch("src.presentation.web.main.initialize_database") as mock_init:
            # Make the initializer raise an exception
            mock_init.side_effect = RuntimeError("Database connection failed")

            # Import should still succeed
            from src.presentation.web.main import app

            # App should still be created
            with TestClient(app) as client:
                # Health check should still work
                response = client.get("/health")
                assert response.status_code == 200

    def test_cors_middleware_configured(self, client: TestClient) -> None:
        """Test that CORS middleware is properly configured."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        # The middleware returns the actual origin when allow_origins=["*"]
        assert (
            response.headers["access-control-allow-origin"] == "http://localhost:3000"
        )
        assert "access-control-allow-methods" in response.headers

    @pytest.mark.parametrize(
        ("endpoint", "expected_status"),
        [
            ("/health", 200),
            ("/", 200),
            ("/nonexistent", 404),
        ],
    )
    def test_endpoint_availability(
        self,
        client: TestClient,
        endpoint: str,
        expected_status: int,
    ) -> None:
        """Test that various endpoints return expected status codes."""
        response = client.get(endpoint)
        assert response.status_code == expected_status

    def test_get_stock_service_dependency_error(self) -> None:
        """Test that get_stock_service raises error when DI container is not
        configured."""
        from fastapi import Request

        from src.presentation.web.routers.stock_router import get_stock_service

        # Create a mock request without di_container in app.state
        mock_request = Mock(spec=Request)
        mock_request.app = Mock()
        mock_request.app.state = Mock(spec=[])  # No di_container attribute

        # Should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            _ = get_stock_service(mock_request)

        assert str(exc_info.value) == "DI container not configured in app state"

    def test_get_stock_service_dependency_success(self) -> None:
        """Test that get_stock_service returns service when DI container exists."""
        from fastapi import Request

        from dependency_injection.di_container import DIContainer
        from src.application.interfaces.stock_service import IStockApplicationService
        from src.presentation.web.routers.stock_router import get_stock_service

        # Create mocks
        mock_service = Mock(spec=IStockApplicationService)
        mock_container = Mock(spec=DIContainer)
        mock_container.resolve.return_value = mock_service

        # Create a mock request with di_container in app.state
        mock_request = Mock(spec=Request)
        mock_request.app = Mock()
        mock_request.app.state = Mock()
        mock_request.app.state.di_container = mock_container

        # Call the dependency
        result = get_stock_service(mock_request)

        # Verify it returns the service from the container
        assert result is mock_service
        mock_container.resolve.assert_called_once_with(IStockApplicationService)
