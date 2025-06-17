"""
Tests for JournalDB database operations.

This module tests the trading journal functionality, which allows users
to record thoughts, observations, and notes about their trading activities.
The journal is flexible - entries can be general observations or linked
to specific stocks, portfolios, or transactions.
"""

import pytest
from datetime import date, timedelta
from utils.database import (
    JournalDB,
    StockDB,
    PortfolioDB,
    StockTransactionDB,
    get_db_connection,
)


class TestJournalDB:
    """Test suite for JournalDB operations."""

    @pytest.fixture
    def setup_related_data(self, test_db):
        """
        Create stocks, portfolios, and transactions for journal tests.

        This provides all the entities that journal entries can reference,
        demonstrating the flexible relationship model.
        """
        # Create a stock
        stock_id = StockDB.create(symbol="AAPL", name="Apple Inc.", grade="A")

        # Create a portfolio
        portfolio_id = PortfolioDB.create(name="Main Portfolio", max_positions=10)

        # Create a transaction
        transaction_id = StockTransactionDB.create(
            portfolio_id=portfolio_id,
            stock_id=stock_id,
            transaction_type="buy",
            quantity=100,
            price=150.00,
            transaction_date=date.today(),
        )

        return {
            "stock_id": stock_id,
            "portfolio_id": portfolio_id,
            "transaction_id": transaction_id,
        }

    def test_create_general_entry(self, test_db):
        """
        Test creating a general journal entry with no specific references.

        This is useful for market observations, strategy thoughts, or
        general trading notes that don't relate to specific positions.
        """
        entry_date = date.today()
        entry_id = JournalDB.create(
            entry_date=entry_date,
            content="Market showing signs of sector rotation. Tech weakening, financials strengthening.",
        )

        assert isinstance(entry_id, int)
        assert entry_id > 0

        # Verify the entry
        entries = JournalDB.get_recent_entries(limit=1)
        assert len(entries) == 1

        entry = entries[0]
        assert (
            entry["content"]
            == "Market showing signs of sector rotation. Tech weakening, financials strengthening."
        )
        assert entry["stock_id"] is None
        assert entry["portfolio_id"] is None
        assert entry["transaction_id"] is None
        # The LEFT JOINs should result in None for symbol and portfolio_name
        assert entry["symbol"] is None
        assert entry["portfolio_name"] is None

    def test_create_stock_specific_entry(self, test_db, setup_related_data):
        """
        Test creating a journal entry linked to a specific stock.

        This demonstrates how traders can keep notes about individual
        stocks they're watching or holding.
        """
        data = setup_related_data

        entry_id = JournalDB.create(
            entry_date=date.today(),
            content="AAPL breaking out of consolidation pattern. Volume confirming move.",
            stock_id=data["stock_id"],
        )

        # Verify the entry includes stock information
        entries = JournalDB.get_recent_entries(limit=1)
        entry = entries[0]

        assert entry["stock_id"] == data["stock_id"]
        assert entry["symbol"] == "AAPL"  # Joined from stock table
        assert entry["portfolio_id"] is None
        assert entry["transaction_id"] is None

    def test_create_transaction_entry(self, test_db, setup_related_data):
        """
        Test creating a journal entry linked to a specific transaction.

        This is perfect for recording the reasoning behind trades,
        creating an audit trail of trading decisions.
        """
        data = setup_related_data

        entry_id = JournalDB.create(
            entry_date=date.today(),
            content="Bought AAPL on breakout above 150 resistance. Stop loss at 145.",
            stock_id=data["stock_id"],
            portfolio_id=data["portfolio_id"],
            transaction_id=data["transaction_id"],
        )

        # Verify all relationships are preserved
        entries = JournalDB.get_recent_entries(limit=1)
        entry = entries[0]

        assert entry["stock_id"] == data["stock_id"]
        assert entry["portfolio_id"] == data["portfolio_id"]
        assert entry["transaction_id"] == data["transaction_id"]
        assert entry["symbol"] == "AAPL"
        assert entry["portfolio_name"] == "Main Portfolio"

    def test_get_recent_entries_ordering(self, test_db):
        """
        Test that entries are returned in the correct order.

        The query orders by entry_date DESC, created_at DESC to ensure
        most recent entries appear first, with same-day entries ordered
        by creation time.
        """
        # Create entries across different dates
        dates = [
            date.today() - timedelta(days=5),
            date.today() - timedelta(days=3),
            date.today() - timedelta(days=1),
            date.today(),
        ]

        for i, entry_date in enumerate(dates):
            JournalDB.create(entry_date=entry_date, content=f"Entry for {entry_date}")

        # Also create multiple entries for today to test secondary ordering
        import time

        for i in range(3):
            JournalDB.create(entry_date=date.today(), content=f"Today entry {i+1}")
            # Small delay to ensure different created_at times
            time.sleep(0.01)

        # Get recent entries
        entries = JournalDB.get_recent_entries(limit=10)

        # Should have 7 total entries
        assert len(entries) == 7

        # First 4 should be today's entries in reverse creation order
        today_entries = [e for e in entries if e["entry_date"] == str(date.today())]
        assert len(today_entries) == 4
        assert today_entries[0]["content"] == "Today entry 3"  # Most recent
        assert today_entries[1]["content"] == "Today entry 2"
        assert today_entries[2]["content"] == "Today entry 1"
        assert today_entries[3]["content"] == f"Entry for {date.today()}"

    def test_get_recent_entries_limit(self, test_db):
        """
        Test that the limit parameter correctly restricts results.

        This is important for UI performance - we don't want to load
        thousands of journal entries at once.
        """
        # Create 30 entries
        for i in range(30):
            entry_date = date.today() - timedelta(days=i)
            JournalDB.create(entry_date=entry_date, content=f"Entry {i+1}")

        # Test default limit of 20
        entries = JournalDB.get_recent_entries()
        assert len(entries) == 20

        # Test custom limits
        assert len(JournalDB.get_recent_entries(limit=5)) == 5
        assert len(JournalDB.get_recent_entries(limit=50)) == 30  # Only 30 exist

    def test_mixed_entry_types(self, test_db, setup_related_data):
        """
        Test retrieving a mix of different entry types together.

        This verifies that the LEFT JOINs work correctly and don't
        filter out entries that lack certain relationships.
        """
        data = setup_related_data

        # Create different types of entries
        # 1. General market observation
        JournalDB.create(
            entry_date=date.today() - timedelta(days=3),
            content="Fed meeting minutes suggest hawkish stance",
        )

        # 2. Stock-specific entry
        JournalDB.create(
            entry_date=date.today() - timedelta(days=2),
            content="AAPL showing relative strength",
            stock_id=data["stock_id"],
        )

        # 3. Portfolio-specific entry
        JournalDB.create(
            entry_date=date.today() - timedelta(days=1),
            content="Portfolio rebalancing completed",
            portfolio_id=data["portfolio_id"],
        )

        # 4. Full transaction entry
        JournalDB.create(
            entry_date=date.today(),
            content="Executed planned AAPL purchase",
            stock_id=data["stock_id"],
            portfolio_id=data["portfolio_id"],
            transaction_id=data["transaction_id"],
        )

        # Get all entries
        entries = JournalDB.get_recent_entries(limit=10)

        # Should have all 4 entries
        assert len(entries) == 4

        # Verify each entry type has appropriate fields
        transaction_entry = entries[0]  # Most recent
        assert transaction_entry["symbol"] == "AAPL"
        assert transaction_entry["portfolio_name"] == "Main Portfolio"
        assert transaction_entry["transaction_id"] is not None

        portfolio_entry = entries[1]
        assert portfolio_entry["symbol"] is None
        assert portfolio_entry["portfolio_name"] == "Main Portfolio"

        stock_entry = entries[2]
        assert stock_entry["symbol"] == "AAPL"
        assert stock_entry["portfolio_name"] is None

        general_entry = entries[3]
        assert general_entry["symbol"] is None
        assert general_entry["portfolio_name"] is None

    def test_long_content(self, test_db):
        """
        Test that journal entries can handle long-form content.

        Traders might write detailed analysis or extended thoughts,
        so the content field should handle substantial text.
        """
        long_content = """
        Today's trading session was particularly interesting. The market opened with a gap up
        following positive earnings from several tech giants. However, by mid-morning, profit-taking
        began to emerge, particularly in the semiconductor sector.

        I noticed unusual volume in financial stocks, which might indicate institutional rotation.
        The banking index broke through its 50-day moving average with conviction. This could be
        the start of a longer-term trend if interest rate expectations continue to rise.

        My current portfolio positioning seems well-aligned with this potential shift. I've been
        gradually reducing tech exposure over the past two weeks and building positions in
        quality financial names. Today's action validates this thesis.

        Key levels to watch tomorrow:
        - SPX: 4520 resistance, 4480 support
        - QQQ: Needs to hold 380 or we could see further weakness
        - XLF: Breaking out, next target 42.50

        Risk management note: Keep position sizes moderate until we see follow-through.
        The market remains news-driven and volatile.
        """

        entry_id = JournalDB.create(
            entry_date=date.today(), content=long_content.strip()
        )

        # Verify the full content is stored and retrieved
        entries = JournalDB.get_recent_entries(limit=1)
        assert entries[0]["content"] == long_content.strip()

    def test_entry_date_flexibility(self, test_db):
        """
        Test that we can create entries for past dates.

        This is important for backfilling journal entries or recording
        thoughts about historical trades for analysis.
        """
        # Create an entry for 30 days ago
        past_date = date.today() - timedelta(days=30)

        entry_id = JournalDB.create(
            entry_date=past_date,
            content="Retrospective: This trade worked out well due to proper position sizing.",
        )

        # Verify it was created with the correct date
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT entry_date FROM journal_entry WHERE id = ?", (entry_id,)
            ).fetchone()
            assert row["entry_date"] == str(past_date)

    def test_update_timestamp_trigger(self, test_db):
        """
        Test that the updated_at timestamp trigger works for journal entries.

        This ensures we can track when entries are modified, which is
        important for audit trails.
        """
        import time
        from datetime import datetime

        # Create an entry
        entry_id = JournalDB.create(entry_date=date.today(), content="Original content")

        # Get the initial timestamps
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT created_at, updated_at FROM journal_entry WHERE id = ?",
                (entry_id,),
            ).fetchone()

            # Parse timestamps without timezone conversion for consistency
            created_at = datetime.fromisoformat(row["created_at"].replace("Z", ""))
            initial_updated_at = datetime.fromisoformat(
                row["updated_at"].replace("Z", "")
            )

            # Initially, created_at and updated_at should be the same
            assert created_at == initial_updated_at

            # Wait long enough to ensure different timestamps
            time.sleep(1.1)  # More than 1 second to ensure difference

            conn.execute(
                "UPDATE journal_entry SET content = ? WHERE id = ?",
                ("Updated content", entry_id),
            )
            conn.commit()

            # Check updated_at again
            row = conn.execute(
                "SELECT created_at, updated_at FROM journal_entry WHERE id = ?",
                (entry_id,),
            ).fetchone()

            new_updated_at = datetime.fromisoformat(row["updated_at"].replace("Z", ""))

            # updated_at should be newer than created_at
            assert new_updated_at > created_at
