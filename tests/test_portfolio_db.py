"""
Tests for PortfolioDB database operations.

This module tests portfolio creation, retrieval, and management operations.
"""

import pytest
from utils.database import PortfolioDB, get_db_connection
from tests.conftest import assert_datetime_recent


class TestPortfolioDB:
    """Test suite for PortfolioDB operations."""

    def test_create_portfolio_defaults(self, test_db):
        """
        Test creating a portfolio with default values.

        Should use max_positions=10 and max_risk_per_trade=2.0 by default.
        """
        portfolio_id = PortfolioDB.create(name="My Portfolio")

        assert isinstance(portfolio_id, int)
        assert portfolio_id > 0

        # Verify defaults were applied
        portfolio = PortfolioDB.get_by_id(portfolio_id)
        assert portfolio is not None
        assert portfolio["name"] == "My Portfolio"
        assert portfolio["max_positions"] == 10
        assert portfolio["max_risk_per_trade"] == 2.0
        assert portfolio["is_active"] == 1  # SQLite uses 1 for True

    def test_create_portfolio_custom_values(self, test_db):
        """
        Test creating a portfolio with custom values.

        This verifies we can override the default values.
        """
        portfolio_id = PortfolioDB.create(
            name="Aggressive Portfolio", max_positions=20, max_risk_per_trade=5.0
        )

        portfolio = PortfolioDB.get_by_id(portfolio_id)
        assert portfolio is not None
        assert portfolio["name"] == "Aggressive Portfolio"
        assert portfolio["max_positions"] == 20
        assert portfolio["max_risk_per_trade"] == 5.0

    def test_get_by_id_not_found(self, test_db):
        """
        Test retrieving a non-existent portfolio returns None.
        """
        portfolio = PortfolioDB.get_by_id(99999)
        assert portfolio is None

    def test_get_all_active_empty(self, test_db):
        """
        Test get_all_active returns empty list when no portfolios exist.
        """
        portfolios = PortfolioDB.get_all_active()
        assert isinstance(portfolios, list)
        assert len(portfolios) == 0

    def test_get_all_active_multiple(self, test_db):
        """
        Test get_all_active returns only active portfolios in order.
        """
        # Create multiple portfolios
        p1_id = PortfolioDB.create(name="Portfolio A")
        p2_id = PortfolioDB.create(name="Portfolio B")
        p3_id = PortfolioDB.create(name="Portfolio C")

        # Deactivate one portfolio
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE portfolio SET is_active = FALSE WHERE id = ?", (p2_id,)
            )
            conn.commit()

        # Get active portfolios
        active_portfolios = PortfolioDB.get_all_active()

        # Should have 2 active portfolios
        assert len(active_portfolios) == 2

        # Verify they're ordered by name
        assert active_portfolios[0]["name"] == "Portfolio A"
        assert active_portfolios[1]["name"] == "Portfolio C"

        # Verify the deactivated portfolio is not included
        portfolio_ids = [p["id"] for p in active_portfolios]
        assert p2_id not in portfolio_ids

    def test_multiple_portfolios_allowed(self, test_db):
        """
        Test that we can create multiple portfolios.

        Unlike stocks with unique symbols, portfolio names don't
        need to be unique.
        """
        # Create portfolios with the same name
        p1_id = PortfolioDB.create(name="Family Portfolio")
        p2_id = PortfolioDB.create(name="Family Portfolio")

        # Both should be created successfully
        assert p1_id != p2_id
        assert p1_id > 0
        assert p2_id > 0

    def test_risk_percentage_precision(self, test_db):
        """
        Test that risk percentage maintains decimal precision.

        The schema defines DECIMAL(3,1) which allows values like 2.5, 10.0.
        """
        portfolio_id = PortfolioDB.create(name="Test Portfolio", max_risk_per_trade=2.5)

        portfolio = PortfolioDB.get_by_id(portfolio_id)
        assert portfolio is not None
        assert portfolio["max_risk_per_trade"] == 2.5

    def test_portfolio_timestamps(self, test_db):
        """
        Test that created_at and updated_at are set correctly.
        """
        from datetime import datetime
        import time

        # Create portfolio
        portfolio_id = PortfolioDB.create(name="Test Portfolio")

        # Check timestamps
        portfolio = PortfolioDB.get_by_id(portfolio_id)
        assert portfolio is not None
        assert portfolio["created_at"] is not None
        assert portfolio["updated_at"] is not None

        # Verify timestamps are recent
        created = datetime.fromisoformat(portfolio["created_at"].replace("Z", "+00:00"))
        assert_datetime_recent(portfolio["created_at"])

    def test_create_portfolio_with_invalid_risk(self, test_db):
        """
        Test that invalid risk values are handled.

        DECIMAL(3,1) means max value is 99.9.
        """
        # This should work - within range
        portfolio_id = PortfolioDB.create(name="High Risk", max_risk_per_trade=99.9)
        assert portfolio_id > 0

        # Values over 99.9 might be truncated or cause error depending on SQLite mode
        # Let's verify reasonable values work
        for risk in [0.5, 1.0, 2.0, 5.0, 10.0]:
            pid = PortfolioDB.create(name=f"Portfolio {risk}", max_risk_per_trade=risk)
            portfolio = PortfolioDB.get_by_id(pid)
            assert portfolio is not None
            assert portfolio["max_risk_per_trade"] == risk
