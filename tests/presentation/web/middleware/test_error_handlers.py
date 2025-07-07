"""Tests for error handler middleware edge cases."""

# pyright: reportUnusedFunction=false

from unittest.mock import Mock, patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.presentation.web.middleware.error_handlers import handle_stock_errors


class TestErrorHandlerEdgeCases:
    """Test edge cases in error handler middleware."""

    def test_handle_stock_errors_reraises_http_exception(self) -> None:
        """Test that HTTPException is re-raised without modification."""
        app = FastAPI()

        @app.get("/test")
        @handle_stock_errors
        async def _test_endpoint() -> dict[str, str]:
            """Test endpoint that raises HTTPException."""
            raise HTTPException(status_code=404, detail="Not found")

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 404
        assert response.json() == {"detail": "Not found"}

    @patch("src.presentation.web.middleware.error_handlers.logger")
    def test_handle_stock_errors_logs_unknown_function_name(
        self,
        mock_logger: Mock,
    ) -> None:
        """Test that unknown function names are logged with generic message."""
        app = FastAPI()

        @app.get("/test")
        @handle_stock_errors
        async def _unknown_function_name() -> dict[str, str]:
            """Test endpoint with unknown function name."""
            msg = "Test error"
            raise RuntimeError(msg)

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 500  # Generic exception returns 500
        assert response.json() == {"detail": "An unexpected error occurred"}

        # Verify the generic error log for unknown function name
        mock_logger.error.assert_called_once_with(
            "Unexpected error in %s: %s",
            "_unknown_function_name",
            "Test error",
        )
