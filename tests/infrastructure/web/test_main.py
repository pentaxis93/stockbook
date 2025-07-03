"""Tests for the main FastAPI application."""

import os
from typing import Iterator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient


class TestMainApp:
    """Test suite for the main FastAPI application."""

    @pytest.fixture
    def mock_database_initializer(self) -> Iterator[Mock]:
        """Mock the database initializer to avoid actual database operations."""
        with patch("src.infrastructure.web.main.initialize_database") as mock:
            yield mock

    @pytest.fixture
    def client(self, mock_database_initializer: Mock) -> TestClient:
        """Create a test client for the FastAPI app."""
        # Import here to ensure mocks are in place
        from src.infrastructure.web.main import app

        return TestClient(app)

    def test_app_creation(self, client: TestClient) -> None:
        """Test that the FastAPI app is created successfully."""
        assert client.app is not None
        # Check app info via the API endpoint instead of attributes
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "StockBook API"
        assert data["version"] == "1.0.0"

    def test_database_initialization_on_startup(
        self, mock_database_initializer: Mock
    ) -> None:
        """Test that database is initialized during app startup."""
        # Import and trigger startup by creating the app
        from src.infrastructure.web.main import app

        # Manually trigger startup event
        with TestClient(app):
            # Verify database initializer was called with correct path
            mock_database_initializer.assert_called_once()

            # Get the actual call arguments
            call_args = mock_database_initializer.call_args[0]
            assert len(call_args) == 1

            # Should be called with the database path from environment
            expected_path = os.getenv(
                "DATABASE_PATH", "/app/data/database/stockbook.db"
            )
            assert call_args[0] == expected_path

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
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert "/health" in data["endpoints"]
        assert "/docs" in data["endpoints"]

    def test_database_initialization_error_handling(self) -> None:
        """Test that database initialization errors are logged but don't crash the app."""
        with patch("src.infrastructure.web.main.initialize_database") as mock_init:
            # Make the initializer raise an exception
            mock_init.side_effect = Exception("Database connection failed")

            # Import should still succeed
            from src.infrastructure.web.main import app

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
        "endpoint,expected_status",
        [
            ("/health", 200),
            ("/", 200),
            ("/nonexistent", 404),
        ],
    )
    def test_endpoint_availability(
        self, client: TestClient, endpoint: str, expected_status: int
    ) -> None:
        """Test that various endpoints return expected status codes."""
        response = client.get(endpoint)
        assert response.status_code == expected_status

    def test_stock_service_factory_error_when_di_container_none(self) -> None:
        """Test that stock service factory raises error when DI container is None."""
        from unittest.mock import Mock, patch

        import src.infrastructure.web.main as main_module
        from dependency_injection.di_container import DIContainer
        from src.application.services.stock_application_service import (
            StockApplicationService,
        )

        # Store original container
        original_container = getattr(main_module, "_di_container", None)

        try:
            # Mock the initialization functions
            with patch("src.infrastructure.web.main.initialize_database"):
                with patch(
                    "src.infrastructure.web.main.CompositionRoot.configure"
                ) as mock_configure:
                    # Create a mock container
                    mock_container = Mock(spec=DIContainer)
                    mock_service = Mock(spec=StockApplicationService)
                    mock_container.resolve.return_value = mock_service
                    mock_configure.return_value = mock_container

                    # Import and create the app with test client
                    from src.infrastructure.web.main import app
                    from src.infrastructure.web.routers import stock_router

                    with TestClient(app):
                        # Get the factory that was set during startup
                        factory = getattr(stock_router, "_service_factory", None)

                        assert (
                            factory is not None
                        ), "Factory should have been set during lifespan"

                        # Now force the DI container to be None to test line 70
                        main_module._di_container = None  # type: ignore[attr-defined]

                        # Call the factory - it should raise RuntimeError
                        with pytest.raises(RuntimeError) as exc_info:
                            factory()

                        assert str(exc_info.value) == "DI container not initialized"
        finally:
            # Restore the original container
            if original_container is not None:
                main_module._di_container = original_container  # type: ignore[attr-defined]

    def test_stock_service_factory_returns_service_when_container_exists(
        self, mock_database_initializer: Mock
    ) -> None:
        """Test that stock service factory returns service when DI container exists."""
        # Create a mock container and service
        from dependency_injection.di_container import DIContainer
        from src.application.services.stock_application_service import (
            StockApplicationService,
        )

        mock_service = Mock(spec=StockApplicationService)
        mock_container = Mock(spec=DIContainer)
        mock_container.resolve.return_value = mock_service

        import src.infrastructure.web.main as main_module

        # Temporarily replace the DI container
        original_container = main_module._di_container  # type: ignore[attr-defined]
        try:
            # Use the actual factory that's created during app startup
            from src.infrastructure.web.main import app
            from src.infrastructure.web.routers import stock_router

            with TestClient(app):
                # Now set a valid mock container
                main_module._di_container = mock_container  # type: ignore[attr-defined]

                # Call the factory
                if (
                    hasattr(stock_router, "_service_factory")
                    and stock_router._service_factory  # type: ignore[attr-defined]
                ):
                    result = stock_router._service_factory()  # type: ignore[attr-defined]

                    # Verify it returns the service from the container
                    assert result is mock_service
                    mock_container.resolve.assert_called_once_with(
                        StockApplicationService
                    )
        finally:
            # Restore the original container
            main_module._di_container = original_container  # type: ignore[attr-defined]
