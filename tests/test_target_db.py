"""
Tests for TargetDB database operations.

This module tests the watchlist/target functionality including creating
targets, updating their status, and filtering active targets.
"""

from sqlite3 import IntegrityError

import pytest

from utils.database import PortfolioDB, StockDB, TargetDB


class TestTargetDB:
    """Test suite for TargetDB operations."""

    @pytest.fixture
    def setup_stocks_and_portfolios(self, test_db):
        """
        Create multiple stocks and portfolios for target tests.

        This provides a more complex setup to test filtering and relationships.
        """
        # Create stocks
        stocks = {
            "AAPL": StockDB.create(symbol="AAPL", name="Apple Inc.", grade="A"),
            "MSFT": StockDB.create(symbol="MSFT", name="Microsoft Corp.", grade="A"),
            "GOOGL": StockDB.create(symbol="GOOGL", name="Alphabet Inc.", grade="B"),
        }

        # Create portfolios
        portfolios = {
            "main": PortfolioDB.create(name="Main Portfolio"),
            "secondary": PortfolioDB.create(name="Secondary Portfolio"),
        }

        return {"stocks": stocks, "portfolios": portfolios}

    def test_create_target_minimal(self, test_db, setup_stocks_and_portfolios):
        """
        Test creating a target with required fields only.

        This verifies basic target creation without optional notes.
        """
        setup = setup_stocks_and_portfolios

        target_id = TargetDB.create(
            stock_id=setup["stocks"]["AAPL"],
            portfolio_id=setup["portfolios"]["main"],
            pivot_price=175.50,
            failure_price=165.00,
        )

        assert isinstance(target_id, int)
        assert target_id > 0

    def test_create_target_with_notes(self, test_db, setup_stocks_and_portfolios):
        """
        Test creating a target with all fields including notes.

        This ensures optional fields are properly stored.
        """
        setup = setup_stocks_and_portfolios

        target_id = TargetDB.create(
            stock_id=setup["stocks"]["MSFT"],
            portfolio_id=setup["portfolios"]["main"],
            pivot_price=380.00,
            failure_price=365.00,
            notes="Breakout from consolidation pattern",
        )

        # Verify by retrieving active targets
        targets = TargetDB.get_active_targets()
        assert len(targets) == 1
        assert targets[0]["notes"] == "Breakout from consolidation pattern"

    def test_get_active_targets_all(self, test_db, setup_stocks_and_portfolios):
        """
        Test retrieving all active targets across portfolios.

        This verifies the join operations and default status filtering.
        """
        setup = setup_stocks_and_portfolios

        # Create targets for different stocks and portfolios
        target_ids = []

        # Target 1: AAPL in main portfolio
        target_ids.append(
            TargetDB.create(
                stock_id=setup["stocks"]["AAPL"],
                portfolio_id=setup["portfolios"]["main"],
                pivot_price=175.00,
                failure_price=165.00,
            )
        )

        # Target 2: MSFT in main portfolio
        target_ids.append(
            TargetDB.create(
                stock_id=setup["stocks"]["MSFT"],
                portfolio_id=setup["portfolios"]["main"],
                pivot_price=380.00,
                failure_price=365.00,
            )
        )

        # Target 3: GOOGL in secondary portfolio
        target_ids.append(
            TargetDB.create(
                stock_id=setup["stocks"]["GOOGL"],
                portfolio_id=setup["portfolios"]["secondary"],
                pivot_price=150.00,
                failure_price=140.00,
            )
        )

        # Get all active targets
        targets = TargetDB.get_active_targets()

        # Should have all 3 targets
        assert len(targets) == 3

        # Verify they're ordered by symbol
        symbols = [t["symbol"] for t in targets]
        assert symbols == ["AAPL", "GOOGL", "MSFT"]

        # Verify joined fields are present
        for target in targets:
            assert "symbol" in target
            assert "stock_name" in target
            assert "portfolio_name" in target
            assert target["status"] == "active"  # Default status

    def test_get_active_targets_by_portfolio(
        self, test_db, setup_stocks_and_portfolios
    ):
        """
        Test filtering active targets by portfolio.

        This ensures the portfolio filtering works correctly.
        """
        setup = setup_stocks_and_portfolios

        # Create targets in different portfolios
        TargetDB.create(
            stock_id=setup["stocks"]["AAPL"],
            portfolio_id=setup["portfolios"]["main"],
            pivot_price=175.00,
            failure_price=165.00,
        )

        TargetDB.create(
            stock_id=setup["stocks"]["MSFT"],
            portfolio_id=setup["portfolios"]["main"],
            pivot_price=380.00,
            failure_price=365.00,
        )

        TargetDB.create(
            stock_id=setup["stocks"]["GOOGL"],
            portfolio_id=setup["portfolios"]["secondary"],
            pivot_price=150.00,
            failure_price=140.00,
        )

        # Get targets for main portfolio only
        main_targets = TargetDB.get_active_targets(
            portfolio_id=setup["portfolios"]["main"]
        )

        # Should have 2 targets
        assert len(main_targets) == 2
        assert all(t["portfolio_name"] == "Main Portfolio" for t in main_targets)

        # Get targets for secondary portfolio
        secondary_targets = TargetDB.get_active_targets(
            portfolio_id=setup["portfolios"]["secondary"]
        )

        # Should have 1 target
        assert len(secondary_targets) == 1
        assert secondary_targets[0]["symbol"] == "GOOGL"

    def test_update_status(self, test_db, setup_stocks_and_portfolios):
        """
        Test updating target status through different states.

        This verifies the status workflow and constraint checking.
        """
        setup = setup_stocks_and_portfolios

        # Create a target
        target_id = TargetDB.create(
            stock_id=setup["stocks"]["AAPL"],
            portfolio_id=setup["portfolios"]["main"],
            pivot_price=175.00,
            failure_price=165.00,
        )

        # Test all valid status transitions
        for status in ["hit", "failed", "cancelled", "active"]:
            success = TargetDB.update_status(target_id, status)
            assert success is True

            # Verify the status was updated
            if status == "active":
                targets = TargetDB.get_active_targets()
                assert len(targets) == 1
                assert targets[0]["id"] == target_id
            else:
                # Non-active statuses shouldn't appear in active targets
                targets = TargetDB.get_active_targets()
                assert len(targets) == 0

    def test_status_filtering(self, test_db, setup_stocks_and_portfolios):
        """
        Test that only active targets are returned by get_active_targets.

        This ensures non-active targets are properly filtered out.
        """
        setup = setup_stocks_and_portfolios

        # Create multiple targets with different statuses
        active_id = TargetDB.create(
            stock_id=setup["stocks"]["AAPL"],
            portfolio_id=setup["portfolios"]["main"],
            pivot_price=175.00,
            failure_price=165.00,
        )

        hit_id = TargetDB.create(
            stock_id=setup["stocks"]["MSFT"],
            portfolio_id=setup["portfolios"]["main"],
            pivot_price=380.00,
            failure_price=365.00,
        )
        TargetDB.update_status(hit_id, "hit")

        failed_id = TargetDB.create(
            stock_id=setup["stocks"]["GOOGL"],
            portfolio_id=setup["portfolios"]["main"],
            pivot_price=150.00,
            failure_price=140.00,
        )
        TargetDB.update_status(failed_id, "failed")

        # Get active targets
        active_targets = TargetDB.get_active_targets()

        # Should only have 1 active target
        assert len(active_targets) == 1
        assert active_targets[0]["id"] == active_id
        assert active_targets[0]["symbol"] == "AAPL"

    def test_multiple_targets_same_stock(self, test_db, setup_stocks_and_portfolios):
        """
        Test that we can have multiple targets for the same stock.

        This is useful for different price levels or portfolios.
        """
        setup = setup_stocks_and_portfolios

        # Create multiple targets for AAPL
        target1_id = TargetDB.create(
            stock_id=setup["stocks"]["AAPL"],
            portfolio_id=setup["portfolios"]["main"],
            pivot_price=175.00,
            failure_price=165.00,
            notes="First resistance level",
        )

        target2_id = TargetDB.create(
            stock_id=setup["stocks"]["AAPL"],
            portfolio_id=setup["portfolios"]["main"],
            pivot_price=185.00,
            failure_price=175.00,
            notes="Second resistance level",
        )

        target3_id = TargetDB.create(
            stock_id=setup["stocks"]["AAPL"],
            portfolio_id=setup["portfolios"]["secondary"],
            pivot_price=180.00,
            failure_price=170.00,
            notes="Different portfolio target",
        )

        # All should be created successfully
        assert target1_id != target2_id != target3_id

        # Get all active targets
        targets = TargetDB.get_active_targets()
        assert len(targets) == 3

        # All should be for AAPL
        assert all(t["symbol"] == "AAPL" for t in targets)

    def test_pivot_failure_price_validation(self, test_db, setup_stocks_and_portfolios):
        """
        Test that pivot and failure prices are stored correctly.

        Note: The schema doesn't enforce pivot > failure, but the app logic should.
        """
        setup = setup_stocks_and_portfolios

        # Create target with decimal prices
        target_id = TargetDB.create(
            stock_id=setup["stocks"]["AAPL"],
            portfolio_id=setup["portfolios"]["main"],
            pivot_price=175.55,
            failure_price=165.25,
        )

        # Retrieve and verify precision is maintained
        targets = TargetDB.get_active_targets()
        assert len(targets) == 1
        assert targets[0]["pivot_price"] == 175.55
        assert targets[0]["failure_price"] == 165.25

    def test_foreign_key_constraints(self, test_db):
        """
        Test that foreign key constraints are enforced for targets.

        Targets must reference valid stocks and portfolios.
        """
        # Try to create target with non-existent stock
        with pytest.raises(IntegrityError):
            TargetDB.create(
                stock_id=99999,  # Non-existent
                portfolio_id=1,
                pivot_price=100.00,
                failure_price=90.00,
            )

        # Try to create target with non-existent portfolio
        stock_id = StockDB.create(symbol="TEST", name="Test Stock")
        with pytest.raises(IntegrityError):
            TargetDB.create(
                stock_id=stock_id,
                portfolio_id=99999,  # Non-existent
                pivot_price=100.00,
                failure_price=90.00,
            )
