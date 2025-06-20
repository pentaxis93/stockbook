"""
Tests for Transaction domain entity.

Following TDD approach - these tests define the expected behavior
of the rich Transaction entity with business logic.
"""

from datetime import date
from decimal import Decimal

import pytest

from src.domain.entities.transaction_entity import TransactionEntity
from src.domain.value_objects import Money, Notes, Quantity
from src.domain.value_objects.transaction_type import TransactionType


class TestTransactionEntity:
    """Test suite for Transaction domain entity."""

    def test_create_transaction_with_value_objects(self):
        """Should create Transaction entity with value objects only."""
        portfolio_id = 1
        stock_id = 2
        transaction_type = TransactionType("buy")
        quantity = Quantity(100)
        price = Money(Decimal("150.25"))
        transaction_date = date(2024, 1, 15)
        notes = Notes("Initial purchase")

        transaction = TransactionEntity(
            portfolio_id=portfolio_id,
            stock_id=stock_id,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            transaction_date=transaction_date,
            notes=notes,
        )

        assert transaction.portfolio_id == portfolio_id
        assert transaction.stock_id == stock_id
        assert transaction.transaction_type == transaction_type
        assert transaction.quantity == quantity
        assert transaction.price == price
        assert transaction.transaction_date == transaction_date
        assert transaction.notes == notes
        assert transaction.id is None  # Not yet persisted

    def test_create_transaction_with_minimal_data(self):
        """Should create Transaction with only required fields."""
        portfolio_id = 1
        stock_id = 2
        transaction_type = TransactionType("sell")
        quantity = Quantity(50)
        price = Money(Decimal("175.50"))
        transaction_date = date(2024, 2, 1)

        transaction = TransactionEntity(
            portfolio_id=portfolio_id,
            stock_id=stock_id,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            transaction_date=transaction_date,
        )

        assert transaction.portfolio_id == portfolio_id
        assert transaction.stock_id == stock_id
        assert transaction.transaction_type == transaction_type
        assert transaction.quantity == quantity
        assert transaction.price == price
        assert transaction.transaction_date == transaction_date
        assert transaction.notes.value == ""  # Notes defaults to empty

    def test_transaction_stores_value_objects(self):
        """Should store and return value objects directly."""
        transaction_type = TransactionType("buy")
        quantity = Quantity(75)
        price = Money(Decimal("200.00"))
        notes = Notes("Test transaction")

        transaction = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            transaction_date=date.today(),
            notes=notes,
        )

        # Should return the exact same value objects
        assert transaction.transaction_type is transaction_type
        assert transaction.quantity is quantity
        assert transaction.price is price
        assert transaction.notes is notes

        # String access through value property
        assert transaction.transaction_type.value == "buy"
        assert transaction.quantity.value == 75
        assert transaction.price.amount == Decimal("200.00")
        assert transaction.notes.value == "Test transaction"

    def test_create_transaction_with_none_notes_allowed(self):
        """Should allow creating transaction with None for notes."""
        transaction = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
            notes=None,
        )

        assert transaction.notes.value == ""  # Notes defaults to empty when None

    def test_create_transaction_with_invalid_transaction_type_raises_error(self):
        """Should raise error for invalid transaction type through TransactionType value object."""
        with pytest.raises(
            ValueError, match="Transaction type must be 'buy' or 'sell'"
        ):
            TransactionType("transfer")  # Error happens at TransactionType construction

    def test_create_transaction_with_invalid_portfolio_id_raises_error(self):
        """Should raise error for invalid portfolio ID."""
        with pytest.raises(ValueError, match="Portfolio ID must be positive"):
            TransactionEntity(
                portfolio_id=0,  # Invalid
                stock_id=1,
                transaction_type=TransactionType("buy"),
                quantity=Quantity(100),
                price=Money(Decimal("100.00")),
                transaction_date=date.today(),
            )

    def test_create_transaction_with_invalid_stock_id_raises_error(self):
        """Should raise error for invalid stock ID."""
        with pytest.raises(ValueError, match="Stock ID must be positive"):
            TransactionEntity(
                portfolio_id=1,
                stock_id=-1,  # Invalid
                transaction_type=TransactionType("buy"),
                quantity=Quantity(100),
                price=Money(Decimal("100.00")),
                transaction_date=date.today(),
            )

    def test_transaction_equality(self):
        """Should compare transactions based on business identity."""
        transaction1 = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date(2024, 1, 1),
        )

        transaction2 = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date(2024, 1, 1),
        )

        transaction3 = TransactionEntity(
            portfolio_id=2,  # Different portfolio
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date(2024, 1, 1),
        )

        # Transactions with same attributes should be equal
        assert transaction1 == transaction2
        assert transaction1 != transaction3

    def test_transaction_string_representation(self):
        """Should have meaningful string representation."""
        transaction = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("150.50")),
            transaction_date=date(2024, 1, 15),
        )

        expected = "buy 100 @ $150.50 on 2024-01-15"
        assert str(transaction) == expected

    def test_transaction_repr(self):
        """Should have detailed repr representation."""
        transaction = TransactionEntity(
            portfolio_id=1,
            stock_id=2,
            transaction_type=TransactionType("sell"),
            quantity=Quantity(50),
            price=Money(Decimal("200.00")),
            transaction_date=date(2024, 2, 1),
        )

        expected = "TransactionEntity(portfolio_id=1, stock_id=2, type='sell', quantity=50, price=$200.00)"
        assert repr(transaction) == expected

    def test_calculate_total_value(self):
        """Should calculate total transaction value."""
        transaction = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("150.50")),
            transaction_date=date.today(),
        )

        total_value = transaction.calculate_total_value()

        assert total_value == Money(Decimal("15050.00"))
        assert isinstance(total_value, Money)

    def test_is_buy_transaction(self):
        """Should check if transaction is a buy."""
        buy_transaction = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
        )

        sell_transaction = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("sell"),
            quantity=Quantity(50),
            price=Money(Decimal("110.00")),
            transaction_date=date.today(),
        )

        assert buy_transaction.is_buy() is True
        assert sell_transaction.is_buy() is False

    def test_is_sell_transaction(self):
        """Should check if transaction is a sell."""
        buy_transaction = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
        )

        sell_transaction = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("sell"),
            quantity=Quantity(50),
            price=Money(Decimal("110.00")),
            transaction_date=date.today(),
        )

        assert buy_transaction.is_sell() is False
        assert sell_transaction.is_sell() is True

    def test_has_notes(self):
        """Should check if transaction has notes."""
        transaction_with_notes = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
            notes=Notes("Important transaction"),
        )

        transaction_without_notes = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
        )

        assert transaction_with_notes.has_notes() is True
        assert transaction_without_notes.has_notes() is False

    def test_set_id(self):
        """Should allow setting ID (for persistence layer)."""
        transaction = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
        )

        assert transaction.id is None

        transaction.set_id(123)
        assert transaction.id == 123

    def test_set_id_with_invalid_id_raises_error(self):
        """Should raise error for invalid ID."""
        transaction = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
        )

        with pytest.raises(ValueError, match="ID must be a positive integer"):
            transaction.set_id(0)

        with pytest.raises(ValueError, match="ID must be a positive integer"):
            transaction.set_id(-1)

        with pytest.raises(ValueError, match="ID must be a positive integer"):
            transaction.set_id("123")

    def test_set_id_when_already_set_raises_error(self):
        """Should raise error when trying to change existing ID."""
        transaction = TransactionEntity(
            portfolio_id=1,
            stock_id=1,
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
        )

        transaction.set_id(123)

        with pytest.raises(ValueError, match="ID is already set and cannot be changed"):
            transaction.set_id(456)


class TestTransactionType:
    """Test TransactionType value object validation."""

    def test_valid_transaction_types_accepted(self):
        """Test that valid transaction types are accepted."""
        valid_types = ["buy", "sell"]
        for transaction_type in valid_types:
            trans_type = TransactionType(transaction_type)
            assert trans_type.value == transaction_type

    def test_case_insensitive_transaction_types(self):
        """Test that transaction types are case insensitive."""
        trans_type1 = TransactionType("BUY")
        trans_type2 = TransactionType("Buy")
        trans_type3 = TransactionType("buy")

        assert trans_type1.value == "buy"
        assert trans_type2.value == "buy"
        assert trans_type3.value == "buy"

    def test_invalid_transaction_types_rejected(self):
        """Test that invalid transaction types are rejected."""
        invalid_types = ["transfer", "dividend", "split", "", "INVALID"]
        for invalid_type in invalid_types:
            with pytest.raises(ValueError):
                TransactionType(invalid_type)
