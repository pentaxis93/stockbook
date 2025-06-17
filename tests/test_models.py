"""
Tests for Pydantic data models
Following TDD approach - these tests will initially fail until models are implemented
"""

from datetime import date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from models import (JournalEntry, Portfolio, PortfolioBalance, Stock, Target,
                    Transaction)


class TestStockModel:
    """Test Stock Pydantic model with symbol validation and grade constraints"""

    def test_valid_stock_creation(self):
        """Test creating a valid stock with all fields"""
        stock = Stock(
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes="Great company",
        )
        assert stock.symbol == "AAPL"
        assert stock.name == "Apple Inc."
        assert stock.industry_group == "Technology"
        assert stock.grade == "A"
        assert stock.notes == "Great company"

    def test_minimal_stock_creation(self):
        """Test creating stock with only required fields"""
        stock = Stock(symbol="MSFT", name="Microsoft Corporation")
        assert stock.symbol == "MSFT"
        assert stock.name == "Microsoft Corporation"
        assert stock.industry_group is None
        assert stock.grade is None
        assert stock.notes is None

    def test_invalid_grade_rejected(self):
        """Test that invalid grades are rejected"""
        with pytest.raises(ValidationError, match="grade"):
            Stock(symbol="AAPL", name="Apple Inc.", grade="D")

    def test_valid_grades_accepted(self):
        """Test that valid grades A, B, C are accepted"""
        for grade in ["A", "B", "C"]:
            stock = Stock(symbol="TEST", name="Test Stock", grade=grade)
            assert stock.grade == grade

    def test_empty_symbol_rejected(self):
        """Test that empty symbol is rejected"""
        with pytest.raises(ValidationError, match="symbol"):
            Stock(symbol="", name="Test Stock")

    def test_empty_name_rejected(self):
        """Test that empty name is rejected"""
        with pytest.raises(ValidationError, match="name"):
            Stock(symbol="TEST", name="")

    def test_symbol_format_validation(self):
        """Test symbol format validation (uppercase letters only)"""
        # Valid symbols
        valid_symbols = ["AAPL", "MSFT", "BRK", "ABC"]
        for symbol in valid_symbols:
            stock = Stock(symbol=symbol, name="Test Stock")
            assert stock.symbol == symbol

        # Invalid symbols should be rejected
        invalid_symbols = ["aapl", "123", "AA-PL", "TOOLONG"]
        for symbol in invalid_symbols:
            with pytest.raises(ValidationError, match="symbol"):
                Stock(symbol=symbol, name="Test Stock")


class TestPortfolioModel:
    """Test Portfolio Pydantic model with name validation and risk percentage limits"""

    def test_valid_portfolio_creation(self):
        """Test creating a valid portfolio with all fields"""
        portfolio = Portfolio(
            name="My Portfolio",
            max_positions=15,
            max_risk_per_trade=1.5,
            is_active=True,
        )
        assert portfolio.name == "My Portfolio"
        assert portfolio.max_positions == 15
        assert portfolio.max_risk_per_trade == 1.5
        assert portfolio.is_active is True

    def test_default_values(self):
        """Test portfolio default values"""
        portfolio = Portfolio(name="Test Portfolio")
        assert portfolio.max_positions == 10
        assert portfolio.max_risk_per_trade == 2.0
        assert portfolio.is_active is True

    def test_empty_name_rejected(self):
        """Test that empty name is rejected"""
        with pytest.raises(ValidationError, match="name"):
            Portfolio(name="")

    def test_negative_max_positions_rejected(self):
        """Test that negative max_positions is rejected"""
        with pytest.raises(ValidationError, match="max_positions"):
            Portfolio(name="Test", max_positions=-1)

    def test_zero_max_positions_rejected(self):
        """Test that zero max_positions is rejected"""
        with pytest.raises(ValidationError, match="max_positions"):
            Portfolio(name="Test", max_positions=0)

    def test_excessive_max_positions_rejected(self):
        """Test that excessive max_positions is rejected"""
        with pytest.raises(ValidationError, match="max_positions"):
            Portfolio(name="Test", max_positions=101)

    def test_negative_risk_rejected(self):
        """Test that negative risk percentage is rejected"""
        with pytest.raises(ValidationError, match="max_risk_per_trade"):
            Portfolio(name="Test", max_risk_per_trade=-0.1)

    def test_excessive_risk_rejected(self):
        """Test that excessive risk percentage is rejected"""
        with pytest.raises(ValidationError, match="max_risk_per_trade"):
            Portfolio(name="Test", max_risk_per_trade=25.1)


class TestTransactionModel:
    """Test Transaction Pydantic model with price/quantity validation and date handling"""

    def test_valid_buy_transaction(self):
        """Test creating a valid buy transaction"""
        transaction = Transaction(
            portfolio_id=1,
            stock_id=1,
            type="buy",
            quantity=100,
            price=Decimal("150.25"),
            transaction_date=date(2024, 1, 15),
            notes="Initial purchase",
        )
        assert transaction.type == "buy"
        assert transaction.quantity == 100
        assert transaction.price == Decimal("150.25")
        assert transaction.transaction_date == date(2024, 1, 15)

    def test_valid_sell_transaction(self):
        """Test creating a valid sell transaction"""
        transaction = Transaction(
            portfolio_id=1,
            stock_id=1,
            type="sell",
            quantity=50,
            price=Decimal("175.00"),
            transaction_date=date(2024, 2, 15),
        )
        assert transaction.type == "sell"
        assert transaction.quantity == 50
        assert transaction.price == Decimal("175.00")

    def test_invalid_transaction_type_rejected(self):
        """Test that invalid transaction types are rejected"""
        with pytest.raises(ValidationError, match="type"):
            Transaction(
                portfolio_id=1,
                stock_id=1,
                type="transfer",
                quantity=100,
                price=Decimal("150.00"),
                transaction_date=date.today(),
            )

    def test_negative_quantity_rejected(self):
        """Test that negative quantity is rejected"""
        with pytest.raises(ValidationError, match="quantity"):
            Transaction(
                portfolio_id=1,
                stock_id=1,
                type="buy",
                quantity=-100,
                price=Decimal("150.00"),
                transaction_date=date.today(),
            )

    def test_zero_quantity_rejected(self):
        """Test that zero quantity is rejected"""
        with pytest.raises(ValidationError, match="quantity"):
            Transaction(
                portfolio_id=1,
                stock_id=1,
                type="buy",
                quantity=0,
                price=Decimal("150.00"),
                transaction_date=date.today(),
            )

    def test_negative_price_rejected(self):
        """Test that negative price is rejected"""
        with pytest.raises(ValidationError, match="price"):
            Transaction(
                portfolio_id=1,
                stock_id=1,
                type="buy",
                quantity=100,
                price=Decimal("-150.00"),
                transaction_date=date.today(),
            )

    def test_zero_price_rejected(self):
        """Test that zero price is rejected"""
        with pytest.raises(ValidationError, match="price"):
            Transaction(
                portfolio_id=1,
                stock_id=1,
                type="buy",
                quantity=100,
                price=Decimal("0.00"),
                transaction_date=date.today(),
            )

    def test_future_date_rejected(self):
        """Test that future dates are rejected"""
        from datetime import timedelta

        future_date = date.today() + timedelta(days=1)

        with pytest.raises(ValidationError, match="transaction_date"):
            Transaction(
                portfolio_id=1,
                stock_id=1,
                type="buy",
                quantity=100,
                price=Decimal("150.00"),
                transaction_date=future_date,
            )


class TestTargetModel:
    """Test Target Pydantic model with price relationship validation"""

    def test_valid_target_creation(self):
        """Test creating a valid target"""
        target = Target(
            stock_id=1,
            portfolio_id=1,
            pivot_price=Decimal("175.00"),
            failure_price=Decimal("140.00"),
            notes="Breakout target",
            status="active",
        )
        assert target.pivot_price == Decimal("175.00")
        assert target.failure_price == Decimal("140.00")
        assert target.status == "active"

    def test_default_status(self):
        """Test default status is active"""
        target = Target(
            stock_id=1,
            portfolio_id=1,
            pivot_price=Decimal("175.00"),
            failure_price=Decimal("140.00"),
        )
        assert target.status == "active"

    def test_invalid_status_rejected(self):
        """Test that invalid status values are rejected"""
        with pytest.raises(ValidationError, match="status"):
            Target(
                stock_id=1,
                portfolio_id=1,
                pivot_price=Decimal("175.00"),
                failure_price=Decimal("140.00"),
                status="pending",
            )

    def test_valid_statuses_accepted(self):
        """Test that all valid statuses are accepted"""
        valid_statuses = ["active", "hit", "failed", "cancelled"]
        for status in valid_statuses:
            target = Target(
                stock_id=1,
                portfolio_id=1,
                pivot_price=Decimal("175.00"),
                failure_price=Decimal("140.00"),
                status=status,
            )
            assert target.status == status

    def test_pivot_price_must_be_above_failure_price(self):
        """Test that pivot price must be greater than failure price"""
        with pytest.raises(
            ValidationError, match="Pivot price must be greater than failure price"
        ):
            Target(
                stock_id=1,
                portfolio_id=1,
                pivot_price=Decimal("140.00"),
                failure_price=Decimal("175.00"),
            )

    def test_equal_prices_rejected(self):
        """Test that equal pivot and failure prices are rejected"""
        with pytest.raises(
            ValidationError, match="Pivot price must be greater than failure price"
        ):
            Target(
                stock_id=1,
                portfolio_id=1,
                pivot_price=Decimal("150.00"),
                failure_price=Decimal("150.00"),
            )


class TestPortfolioBalanceModel:
    """Test PortfolioBalance Pydantic model with balance validation and date constraints"""

    def test_valid_balance_creation(self):
        """Test creating a valid portfolio balance"""
        balance = PortfolioBalance(
            portfolio_id=1,
            balance_date=date(2024, 1, 31),
            withdrawals=Decimal("500.00"),
            deposits=Decimal("1000.00"),
            final_balance=Decimal("15000.00"),
            index_change=Decimal("2.5"),
        )
        assert balance.portfolio_id == 1
        assert balance.balance_date == date(2024, 1, 31)
        assert balance.withdrawals == Decimal("500.00")
        assert balance.deposits == Decimal("1000.00")
        assert balance.final_balance == Decimal("15000.00")
        assert balance.index_change == Decimal("2.5")

    def test_default_values(self):
        """Test default values for withdrawals and deposits"""
        balance = PortfolioBalance(
            portfolio_id=1,
            balance_date=date(2024, 1, 31),
            final_balance=Decimal("15000.00"),
        )
        assert balance.withdrawals == Decimal("0.00")
        assert balance.deposits == Decimal("0.00")
        assert balance.index_change is None

    def test_negative_withdrawals_rejected(self):
        """Test that negative withdrawals are rejected"""
        with pytest.raises(ValidationError, match="withdrawals"):
            PortfolioBalance(
                portfolio_id=1,
                balance_date=date.today(),
                withdrawals=Decimal("-100.00"),
                final_balance=Decimal("15000.00"),
            )

    def test_negative_deposits_rejected(self):
        """Test that negative deposits are rejected"""
        with pytest.raises(ValidationError, match="deposits"):
            PortfolioBalance(
                portfolio_id=1,
                balance_date=date.today(),
                deposits=Decimal("-100.00"),
                final_balance=Decimal("15000.00"),
            )

    def test_future_date_rejected(self):
        """Test that future dates are rejected"""
        from datetime import timedelta

        future_date = date.today() + timedelta(days=1)

        with pytest.raises(ValidationError, match="balance_date"):
            PortfolioBalance(
                portfolio_id=1,
                balance_date=future_date,
                final_balance=Decimal("15000.00"),
            )


class TestJournalEntryModel:
    """Test JournalEntry Pydantic model with content validation"""

    def test_valid_journal_entry_creation(self):
        """Test creating a valid journal entry"""
        entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content="Bought AAPL at support level. Good risk/reward setup.",
            stock_id=1,
            portfolio_id=1,
            transaction_id=1,
        )
        assert entry.entry_date == date(2024, 1, 15)
        assert "AAPL" in entry.content
        assert entry.stock_id == 1
        assert entry.portfolio_id == 1
        assert entry.transaction_id == 1

    def test_minimal_journal_entry(self):
        """Test creating journal entry with only required fields"""
        entry = JournalEntry(
            entry_date=date.today(), content="Market observation for today."
        )
        assert entry.content == "Market observation for today."
        assert entry.stock_id is None
        assert entry.portfolio_id is None
        assert entry.transaction_id is None

    def test_empty_content_rejected(self):
        """Test that empty content is rejected"""
        with pytest.raises(ValidationError, match="content"):
            JournalEntry(entry_date=date.today(), content="")

    def test_whitespace_only_content_rejected(self):
        """Test that whitespace-only content is rejected"""
        with pytest.raises(ValidationError, match="content"):
            JournalEntry(entry_date=date.today(), content="   \n\t   ")

    def test_future_date_rejected(self):
        """Test that future dates are rejected"""
        from datetime import timedelta

        future_date = date.today() + timedelta(days=1)

        with pytest.raises(ValidationError, match="entry_date"):
            JournalEntry(entry_date=future_date, content="Future entry")

    def test_content_length_validation(self):
        """Test content length limits"""
        # Very long content should be rejected
        very_long_content = "A" * 10001  # Assuming 10000 char limit
        with pytest.raises(ValidationError, match="content"):
            JournalEntry(entry_date=date.today(), content=very_long_content)
