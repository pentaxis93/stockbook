"""
Tests for PortfolioBalanceDB database operations.

This module tests the portfolio balance tracking functionality, which is
crucial for performance measurement and historical tracking.
"""

import pytest
from datetime import date, timedelta
from utils.database import PortfolioBalanceDB, PortfolioDB
from sqlite3 import IntegrityError


class TestPortfolioBalanceDB:
    """Test suite for PortfolioBalanceDB operations."""

    @pytest.fixture
    def portfolio(self, test_db):
        """Create a test portfolio for balance tests."""
        portfolio_id = PortfolioDB.create(
            name="Performance Test Portfolio", max_positions=10
        )
        return portfolio_id

    def test_create_balance_minimal(self, test_db, portfolio):
        """
        Test creating a balance entry with minimal required fields.

        This verifies that withdrawals, deposits, and index_change
        have proper defaults when not specified.
        """
        balance_date = date.today()
        balance_id = PortfolioBalanceDB.create(
            portfolio_id=portfolio, balance_date=balance_date, final_balance=100000.00
        )

        assert isinstance(balance_id, int)
        assert balance_id > 0

        # Verify defaults were applied
        history = PortfolioBalanceDB.get_history(portfolio, limit=1)
        assert len(history) == 1

        balance = history[0]
        assert balance["withdrawals"] == 0
        assert balance["deposits"] == 0
        assert balance["index_change"] is None

    def test_create_balance_complete(self, test_db, portfolio):
        """
        Test creating a balance entry with all fields populated.

        This represents a typical month-end balance update with
        cash flows and market performance tracking.
        """
        balance_date = date.today()
        balance_id = PortfolioBalanceDB.create(
            portfolio_id=portfolio,
            balance_date=balance_date,
            final_balance=105000.00,
            withdrawals=2000.00,
            deposits=5000.00,
            index_change=2.5,  # 2.5% gain in S&P 500
        )

        # Verify all fields were stored
        history = PortfolioBalanceDB.get_history(portfolio, limit=1)
        balance = history[0]

        assert balance["final_balance"] == 105000.00
        assert balance["withdrawals"] == 2000.00
        assert balance["deposits"] == 5000.00
        assert balance["index_change"] == 2.5

    def test_unique_date_constraint(self, test_db, portfolio):
        """
        Test that only one balance entry per date per portfolio is allowed.

        The UNIQUE constraint on (portfolio_id, balance_date) ensures
        we don't have duplicate entries for the same date.
        """
        balance_date = date.today()

        # Create first balance
        PortfolioBalanceDB.create(
            portfolio_id=portfolio, balance_date=balance_date, final_balance=100000.00
        )

        # Attempt to create another for same date should update, not create new
        # This is because we use INSERT OR REPLACE
        balance_id2 = PortfolioBalanceDB.create(
            portfolio_id=portfolio,
            balance_date=balance_date,
            final_balance=101000.00,  # Different balance
        )

        # Should have only one entry for this date
        history = PortfolioBalanceDB.get_history(portfolio, limit=10)
        today_entries = [h for h in history if h["balance_date"] == str(balance_date)]
        assert len(today_entries) == 1

        # And it should have the updated balance
        assert today_entries[0]["final_balance"] == 101000.00

    def test_get_history_ordering(self, test_db, portfolio):
        """
        Test that balance history is returned in descending date order.

        This is important for showing recent performance first in the UI.
        """
        # Create balances for multiple dates
        dates = [
            date.today() - timedelta(days=60),
            date.today() - timedelta(days=30),
            date.today() - timedelta(days=15),
            date.today() - timedelta(days=1),
            date.today(),
        ]

        for i, balance_date in enumerate(dates):
            PortfolioBalanceDB.create(
                portfolio_id=portfolio,
                balance_date=balance_date,
                final_balance=100000.00 + (i * 1000),  # Growing balance
            )

        # Get history
        history = PortfolioBalanceDB.get_history(portfolio, limit=10)

        # Should have all 5 entries
        assert len(history) == 5

        # Verify descending order (most recent first)
        history_dates = [h["balance_date"] for h in history]
        expected_dates = [str(d) for d in reversed(dates)]
        assert history_dates == expected_dates

    def test_get_history_limit(self, test_db, portfolio):
        """
        Test that the limit parameter correctly restricts results.

        This is useful for showing only recent history in dashboards.
        """
        # Create 10 balance entries
        for i in range(10):
            balance_date = date.today() - timedelta(days=i)
            PortfolioBalanceDB.create(
                portfolio_id=portfolio,
                balance_date=balance_date,
                final_balance=100000.00 + (i * 100),
            )

        # Test different limits
        assert len(PortfolioBalanceDB.get_history(portfolio, limit=5)) == 5
        assert len(PortfolioBalanceDB.get_history(portfolio, limit=3)) == 3
        assert (
            len(PortfolioBalanceDB.get_history(portfolio, limit=30)) == 10
        )  # Only 10 exist

    def test_multiple_portfolios_isolation(self, test_db):
        """
        Test that balance entries are properly isolated by portfolio.

        Each portfolio should have its own independent balance history.
        """
        # Create two portfolios
        portfolio1 = PortfolioDB.create(name="Portfolio 1")
        portfolio2 = PortfolioDB.create(name="Portfolio 2")

        # Create balances for both on same dates
        for days_ago in [30, 20, 10, 0]:
            balance_date = date.today() - timedelta(days=days_ago)

            # Portfolio 1 balance
            PortfolioBalanceDB.create(
                portfolio_id=portfolio1,
                balance_date=balance_date,
                final_balance=100000.00 + (days_ago * 100),
            )

            # Portfolio 2 balance (different amounts)
            PortfolioBalanceDB.create(
                portfolio_id=portfolio2,
                balance_date=balance_date,
                final_balance=200000.00 + (days_ago * 200),
            )

        # Get history for each portfolio
        history1 = PortfolioBalanceDB.get_history(portfolio1)
        history2 = PortfolioBalanceDB.get_history(portfolio2)

        # Each should have 4 entries
        assert len(history1) == 4
        assert len(history2) == 4

        # Balances should be different
        assert history1[0]["final_balance"] != history2[0]["final_balance"]

    def test_performance_calculation_data(self, test_db, portfolio):
        """
        Test storing data needed for performance calculations.

        This demonstrates how the balance table supports performance
        measurement by tracking cash flows separately from balance changes.
        """
        # Month 1: Starting balance
        PortfolioBalanceDB.create(
            portfolio_id=portfolio,
            balance_date=date.today() - timedelta(days=60),
            final_balance=100000.00,
            deposits=100000.00,  # Initial deposit
            index_change=0.0,
        )

        # Month 2: Gain with no cash flows
        PortfolioBalanceDB.create(
            portfolio_id=portfolio,
            balance_date=date.today() - timedelta(days=30),
            final_balance=105000.00,  # 5% gain
            withdrawals=0,
            deposits=0,
            index_change=3.2,  # Market was up 3.2%
        )

        # Month 3: Loss with withdrawal
        PortfolioBalanceDB.create(
            portfolio_id=portfolio,
            balance_date=date.today(),
            final_balance=98000.00,
            withdrawals=5000.00,  # Withdrew $5000
            deposits=0,
            index_change=-1.5,  # Market was down 1.5%
        )

        # Get history to verify performance tracking
        history = PortfolioBalanceDB.get_history(portfolio)

        # Most recent entry
        latest = history[0]
        assert latest["final_balance"] == 98000.00
        assert latest["withdrawals"] == 5000.00

        # The actual portfolio return would be calculated as:
        # Start: 105000, End: 98000 + 5000 (withdrawal) = 103000
        # Return: -1.9% vs market -1.5%, so underperformed by 0.4%
        # This calculation would be done in the application layer

    def test_foreign_key_constraint(self, test_db):
        """
        Test that balance entries require a valid portfolio.

        This ensures referential integrity in the database.
        """
        # Try to create balance for non-existent portfolio
        with pytest.raises(IntegrityError):
            PortfolioBalanceDB.create(
                portfolio_id=99999,  # Non-existent
                balance_date=date.today(),
                final_balance=100000.00,
            )

    def test_decimal_precision(self, test_db, portfolio):
        """
        Test that monetary values maintain proper decimal precision.

        Financial applications need exact decimal handling for money.
        """
        balance_id = PortfolioBalanceDB.create(
            portfolio_id=portfolio,
            balance_date=date.today(),
            final_balance=123456.78,
            withdrawals=1234.56,
            deposits=9876.54,
            index_change=12.34,
        )

        # Retrieve and verify precision is maintained
        history = PortfolioBalanceDB.get_history(portfolio, limit=1)
        balance = history[0]

        assert balance["final_balance"] == 123456.78
        assert balance["withdrawals"] == 1234.56
        assert balance["deposits"] == 9876.54
        assert balance["index_change"] == 12.34
