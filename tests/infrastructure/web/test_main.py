"""
Tests for FastAPI application creation and configuration.

Following TDD principles - these tests define the expected behavior
before implementation.
"""

from fastapi import FastAPI


class TestFastAPIAppCreation:
    """Test suite for FastAPI application creation."""

    def test_fastapi_app_creation(self) -> None:
        """Test that FastAPI app can be created."""
        # This test will fail until we implement create_app()
        from src.infrastructure.web.main import create_app

        app = create_app()

        assert app is not None
        assert isinstance(app, FastAPI)
        assert app.title == "StockBook API"
        assert app.version == "1.0.0"

    def test_fastapi_app_has_correct_metadata(self) -> None:
        """Test that FastAPI app has correct metadata."""
        from src.infrastructure.web.main import create_app

        app = create_app()

        assert app.description is not None
        assert "StockBook" in app.description
        assert app.openapi_tags is not None

    def test_fastapi_app_is_reusable(self) -> None:
        """Test that create_app() returns new instances."""
        from src.infrastructure.web.main import create_app

        app1 = create_app()
        app2 = create_app()

        # They should be different instances but have same configuration
        assert app1 is not app2
        assert app1.title == app2.title
