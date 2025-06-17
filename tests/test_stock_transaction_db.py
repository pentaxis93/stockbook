"""
Tests for StockTransactionDB database operations.

This module tests transaction creation, retrieval, and the complex
holdings calculation logic.
"""

import pytest
from datetime import date, datetime, timedelta
from utils.database import StockTransactionDB, StockDB, PortfolioDB
from sqlite3 import IntegrityError


class TestStockTransactionDB:
    """Test suite for StockTransactionDB operations."""

    @pytest.fixture
    def setup_stock_and_portfolio(self, test_db):
        """
        Create a stock and portfolio for transaction tests.

        This fixture provides the prerequisites for creating transactions.
        """
        stock_id = StockDB.create(symbol="AAPL", name="Apple Inc.", grade="A")
        portfolio_id = PortfolioDB.create(name="Test Portfolio", max_positions=10)
        return {"stock_id": stock_id, "portfolio_id": portfolio_id}

    def test_create_buy_transaction(self, test_db, setup_stock_and_portfolio):
        """
        Test creating a buy transaction.

        This tests the basic transaction creation with all required fields.
        """
        setup = setup_stock_and_portfolio
        transaction_date = date.today()

        transaction_id = StockTransactionDB.create(
            portfolio_id=setup["portfolio_id"],
            stock_id=setup["stock_id"],
            transaction_type="buy",
            quantity=100,
            price=150.50,
            transaction_date=transaction_date,
            notes="Initial purchase",
        )

        assert isinstance(transaction_id, int)
        assert transaction_id > 0

    def test_create_sell_transaction(self, test_db, setup_stock_and_portfolio):
        """
        Test creating a sell transaction.

        This verifies we can record both buy and sell transaction types.
        """
        setup = setup_stock_and_portfolio

        # First buy some shares
        StockTransactionDB.create(
            portfolio_id=setup["portfolio_id"],
            stock_id=setup["stock_id"],
            transaction_type="buy",
            quantity=100,
            price=150.00,
            transaction_date=date.today() - timedelta(days=30),
        )

        # Then sell some
        sell_id = StockTransactionDB.create(
            portfolio_id=setup["portfolio_id"],
            stock_id=setup["stock_id"],
            transaction_type="sell",
            quantity=50,
            price=160.00,
            transaction_date=date.today(),
            notes="Taking partial profits",
        )

        assert sell_id > 0

    def test_transaction_type_constraint(self, test_db, setup_stock_and_portfolio):
        """
        Test that only 'buy' and 'sell' transaction types are allowed.

        The schema has a CHECK constraint on the type column.
        """
        setup = setup_stock_and_portfolio

        # Valid types should work
        for trans_type in ["buy", "sell"]:
            trans_id = StockTransactionDB.create(
                portfolio_id=setup["portfolio_id"],
                stock_id=setup["stock_id"],
                transaction_type=trans_type,
                quantity=10,
                price=100.00,
                transaction_date=date.today(),
            )
            assert trans_id > 0

    def test_foreign_key_constraints(self, test_db):
        """
        Test that foreign key constraints are enforced.

        Transactions should require valid portfolio and stock IDs.
        """
        # Try to create transaction with non-existent portfolio
        with pytest.raises(IntegrityError):
            StockTransactionDB.create(
                portfolio_id=99999,  # Non-existent
                stock_id=1,
                transaction_type="buy",
                quantity=100,
                price=50.00,
                transaction_date=date.today(),
            )

    def test_get_portfolio_transactions(self, test_db, setup_stock_and_portfolio):
        """
        Test retrieving all transactions for a portfolio.

        This should return transactions with stock information joined.
        """
        setup = setup_stock_and_portfolio

        # Create multiple transactions
        dates = [
            date.today() - timedelta(days=60),
            date.today() - timedelta(days=30),
            date.today() - timedelta(days=1),
        ]

        for i, trans_date in enumerate(dates):
            StockTransactionDB.create(
                portfolio_id=setup["portfolio_id"],
                stock_id=setup["stock_id"],
                transaction_type="buy" if i % 2 == 0 else "sell",
                quantity=100 + i * 10,
                price=150.00 + i * 5,
                transaction_date=trans_date,
            )

        # Also create a transaction for a different portfolio
        other_portfolio_id = PortfolioDB.create(name="Other Portfolio")
        StockTransactionDB.create(
            portfolio_id=other_portfolio_id,
            stock_id=setup["stock_id"],
            transaction_type="buy",
            quantity=200,
            price=145.00,
            transaction_date=date.today(),
        )

        # Get transactions for our test portfolio
        transactions = StockTransactionDB.get_portfolio_transactions(
            setup["portfolio_id"]
        )

        # Should have 3 transactions (not 4 - excluding other portfolio)
        assert len(transactions) == 3

        # Verify they're ordered by date descending (most recent first)
        assert transactions[0]["transaction_date"] == str(dates[2])
        assert transactions[1]["transaction_date"] == str(dates[1])
        assert transactions[2]["transaction_date"] == str(dates[0])

        # Verify stock information is joined
        assert all(t["symbol"] == "AAPL" for t in transactions)
        assert all(t["stock_name"] == "Apple Inc." for t in transactions)

    def test_get_holdings_single_stock(self, test_db, setup_stock_and_portfolio):
        """
        Test calculating holdings for a single stock.

        This tests the aggregation logic for buy/sell transactions.
        """
        setup = setup_stock_and_portfolio

        # Buy 100 shares at $150
        StockTransactionDB.create(
            portfolio_id=setup["portfolio_id"],
            stock_id=setup["stock_id"],
            transaction_type="buy",
            quantity=100,
            price=150.00,
            transaction_date=date.today() - timedelta(days=30),
        )

        # Buy 50 more shares at $160
        StockTransactionDB.create(
            portfolio_id=setup["portfolio_id"],
            stock_id=setup["stock_id"],
            transaction_type="buy",
            quantity=50,
            price=160.00,
            transaction_date=date.today() - timedelta(days=15),
        )

        # Sell 30 shares at $170
        StockTransactionDB.create(
            portfolio_id=setup["portfolio_id"],
            stock_id=setup["stock_id"],
            transaction_type="sell",
            quantity=30,
            price=170.00,
            transaction_date=date.today(),
        )

        # Get holdings
        holdings = StockTransactionDB.get_holdings(setup["portfolio_id"])

        # Should have 1 holding
        assert len(holdings) == 1

        holding = holdings[0]
        assert holding["symbol"] == "AAPL"
        assert holding["shares"] == 120  # 100 + 50 - 30

        # Cost basis: (100 * 150) + (50 * 160) - (30 * 170)
        # = 15000 + 8000 - 5100 = 17900
        assert holding["cost_basis"] == 17900.00

    def test_get_holdings_multiple_stocks(self, test_db):
        """
        Test calculating holdings for multiple stocks in a portfolio.

        This ensures the GROUP BY logic works correctly.
        """
        # Create portfolio and multiple stocks
        portfolio_id = PortfolioDB.create(name="Diversified Portfolio")

        stocks = {
            "AAPL": StockDB.create(symbol="AAPL", name="Apple Inc.", grade="A"),
            "MSFT": StockDB.create(symbol="MSFT", name="Microsoft Corp.", grade="A"),
            "GOOGL": StockDB.create(symbol="GOOGL", name="Alphabet Inc.", grade="B"),
        }

        # Create transactions for each stock
        for symbol, stock_id in stocks.items():
            # Buy transaction
            StockTransactionDB.create(
                portfolio_id=portfolio_id,
                stock_id=stock_id,
                transaction_type="buy",
                quantity=100,
                price=100.00 * (1 + list(stocks.keys()).index(symbol)),
                transaction_date=date.today(),
            )

        # Sell all GOOGL shares
        StockTransactionDB.create(
            portfolio_id=portfolio_id,
            stock_id=stocks["GOOGL"],
            transaction_type="sell",
            quantity=100,
            price=350.00,
            transaction_date=date.today(),
        )

        # Get holdings
        holdings = StockTransactionDB.get_holdings(portfolio_id)

        # Should have 2 holdings (GOOGL sold out)
        assert len(holdings) == 2

        # Verify holdings are for AAPL and MSFT
        symbols = {h["symbol"] for h in holdings}
        assert symbols == {"AAPL", "MSFT"}

        # Verify stock grades are included
        for holding in holdings:
            assert holding["grade"] == "A"

    def test_get_holdings_sold_out_position(self, test_db, setup_stock_and_portfolio):
        """
        Test that fully sold positions don't appear in holdings.

        The HAVING clause should filter out positions with 0 shares.
        """
        setup = setup_stock_and_portfolio

        # Buy 100 shares
        StockTransactionDB.create(
            portfolio_id=setup["portfolio_id"],
            stock_id=setup["stock_id"],
            transaction_type="buy",
            quantity=100,
            price=150.00,
            transaction_date=date.today() - timedelta(days=10),
        )

        # Sell all 100 shares
        StockTransactionDB.create(
            portfolio_id=setup["portfolio_id"],
            stock_id=setup["stock_id"],
            transaction_type="sell",
            quantity=100,
            price=160.00,
            transaction_date=date.today(),
        )

        # Get holdings
        holdings = StockTransactionDB.get_holdings(setup["portfolio_id"])

        # Should have no holdings
        assert len(holdings) == 0

    def test_get_holdings_empty_portfolio(self, test_db):
        """
        Test getting holdings for a portfolio with no transactions.

        This should return an empty list, not raise an error.
        """
        portfolio_id = PortfolioDB.create(name="Empty Portfolio")
        holdings = StockTransactionDB.get_holdings(portfolio_id)

        assert isinstance(holdings, list)
        assert len(holdings) == 0

    def test_transaction_date_handling(self, test_db, setup_stock_and_portfolio):
        """
        Test that transaction dates are stored and retrieved correctly.

        This is important for historical tracking and reporting.
        """
        setup = setup_stock_and_portfolio
        past_date = date(2024, 1, 15)

        transaction_id = StockTransactionDB.create(
            portfolio_id=setup["portfolio_id"],
            stock_id=setup["stock_id"],
            transaction_type="buy",
            quantity=100,
            price=150.00,
            transaction_date=past_date,
        )

        # Retrieve and verify
        transactions = StockTransactionDB.get_portfolio_transactions(
            setup["portfolio_id"]
        )
        assert len(transactions) == 1
        assert transactions[0]["transaction_date"] == "2024-01-15"
