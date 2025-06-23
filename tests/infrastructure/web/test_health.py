"""
Tests for health check endpoint.

Following TDD principles - these tests define the expected behavior
before implementation.
"""

from fastapi.testclient import TestClient


class TestHealthCheck:
    """Test suite for health check endpoint."""

    def test_health_check_returns_200(self) -> None:
        """Test health check endpoint returns 200 status."""
        from src.infrastructure.web.main import create_app

        client = TestClient(create_app())
        response = client.get("/health")

        assert response.status_code == 200

    def test_health_check_returns_correct_json(self) -> None:
        """Test health check endpoint returns correct JSON structure."""
        from src.infrastructure.web.main import create_app

        client = TestClient(create_app())
        response = client.get("/health")

        assert response.status_code == 200
        json_data = response.json()
        assert json_data == {"status": "healthy", "service": "StockBook API"}

    def test_health_check_content_type(self) -> None:
        """Test health check endpoint returns JSON content type."""
        from src.infrastructure.web.main import create_app

        client = TestClient(create_app())
        response = client.get("/health")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_health_check_with_different_methods(self) -> None:
        """Test health check endpoint only accepts GET requests."""
        from src.infrastructure.web.main import create_app

        client = TestClient(create_app())

        # GET should work
        response = client.get("/health")
        assert response.status_code == 200

        # POST should not be allowed
        response = client.post("/health")
        assert response.status_code == 405  # Method Not Allowed

        # PUT should not be allowed
        response = client.put("/health")
        assert response.status_code == 405  # Method Not Allowed
