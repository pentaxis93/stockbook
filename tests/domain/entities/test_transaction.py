"""
Tests for Transaction domain entity.

Following TDD approach - these tests define the expected behavior
of the rich Transaction entity with business logic.
"""

from datetime import date
from decimal import Decimal

import pytest

from src.domain.entities.transaction import Transaction
from src.domain.value_objects import Money, Notes, Quantity
from src.domain.value_objects.transaction_type import TransactionType


class TestTransaction:
    """Test suite for Transaction domain entity."""

    def test_create_transaction_with_value_objects(self) -> None:
        """Should create Transaction entity with value objects only."""
        portfolio_id = "portfolio-1"
        stock_id = "stock-2"
        transaction_type = TransactionType("buy")
        quantity = Quantity(100)
        price = Money(Decimal("150.25"))
        transaction_date = date(2024, 1, 15)
        notes = Notes("Initial purchase")

        transaction = Transaction(
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
        assert transaction.id is not None  # Generated nanoid
        assert isinstance(transaction.id, str)

    def test_create_transaction_with_minimal_data(self) -> None:
        """Should create Transaction with only required fields."""
        portfolio_id = "portfolio-1"
        stock_id = "stock-2"
        transaction_type = TransactionType("sell")
        quantity = Quantity(50)
        price = Money(Decimal("175.50"))
        transaction_date = date(2024, 2, 1)

        transaction = Transaction(
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

    def test_transaction_stores_value_objects(self) -> None:
        """Should store and return value objects directly."""
        transaction_type = TransactionType("buy")
        quantity = Quantity(75)
        price = Money(Decimal("200.00"))
        notes = Notes("Test transaction")

        transaction = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
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

    def test_create_transaction_with_none_notes_allowed(self) -> None:
        """Should allow creating transaction with None for notes."""
        transaction = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
            notes=None,
        )

        assert transaction.notes.value == ""  # Notes defaults to empty when None

    def test_create_transaction_with_invalid_transaction_type_raises_error(
        self,
    ) -> None:
        """Should raise error for invalid transaction type through TransactionType value object."""
        with pytest.raises(
            ValueError, match="Transaction type must be 'buy' or 'sell'"
        ):
            _ = TransactionType(
                "transfer"
            )  # Error happens at TransactionType construction

    def test_create_transaction_with_invalid_portfolio_id_raises_error(self) -> None:
        """Should raise error for invalid portfolio ID."""
        with pytest.raises(ValueError, match="Portfolio ID must be a non-empty string"):
            _ = Transaction(
                portfolio_id="",  # Invalid empty string
                stock_id="stock-id-1",
                transaction_type=TransactionType("buy"),
                quantity=Quantity(100),
                price=Money(Decimal("100.00")),
                transaction_date=date.today(),
            )

    def test_create_transaction_with_invalid_stock_id_raises_error(self) -> None:
        """Should raise error for invalid stock ID."""
        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            _ = Transaction(
                portfolio_id="portfolio-id-1",
                stock_id="",  # Invalid empty string
                transaction_type=TransactionType("buy"),
                quantity=Quantity(100),
                price=Money(Decimal("100.00")),
                transaction_date=date.today(),
            )

    def test_transaction_equality(self) -> None:
        """Should compare transactions based on business identity."""
        transaction1 = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date(2024, 1, 1),
        )

        transaction2 = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date(2024, 1, 1),
        )

        transaction3 = Transaction(
            portfolio_id="portfolio-id-2",  # Different portfolio
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date(2024, 1, 1),
        )

        # Transactions with same attributes should be equal
        assert transaction1 == transaction2
        assert transaction1 != transaction3

    def test_transaction_string_representation(self) -> None:
        """Should have meaningful string representation."""
        transaction = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("150.50")),
            transaction_date=date(2024, 1, 15),
        )

        expected = "buy 100 @ $150.50 on 2024-01-15"
        assert str(transaction) == expected

    def test_transaction_repr(self) -> None:
        """Should have detailed repr representation."""
        transaction = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-2",
            transaction_type=TransactionType("sell"),
            quantity=Quantity(50),
            price=Money(Decimal("200.00")),
            transaction_date=date(2024, 2, 1),
        )

        expected = "Transaction(portfolio_id=portfolio-id-1, stock_id=stock-id-2, type='sell', quantity=50, price=$200.00)"
        assert repr(transaction) == expected

    def test_calculate_total_value(self) -> None:
        """Should calculate total transaction value."""
        transaction = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("150.50")),
            transaction_date=date.today(),
        )

        total_value = transaction.calculate_total_value()

        assert total_value == Money(Decimal("15050.00"))
        assert isinstance(total_value, Money)

    def test_is_buy_transaction(self) -> None:
        """Should check if transaction is a buy."""
        buy_transaction = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
        )

        sell_transaction = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("sell"),
            quantity=Quantity(50),
            price=Money(Decimal("110.00")),
            transaction_date=date.today(),
        )

        assert buy_transaction.is_buy() is True
        assert sell_transaction.is_buy() is False

    def test_is_sell_transaction(self) -> None:
        """Should check if transaction is a sell."""
        buy_transaction = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
        )

        sell_transaction = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("sell"),
            quantity=Quantity(50),
            price=Money(Decimal("110.00")),
            transaction_date=date.today(),
        )

        assert buy_transaction.is_sell() is False
        assert sell_transaction.is_sell() is True

    def test_has_notes(self) -> None:
        """Should check if transaction has notes."""
        transaction_with_notes = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
            notes=Notes("Important transaction"),
        )

        transaction_without_notes = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
        )

        assert transaction_with_notes.has_notes() is True
        assert transaction_without_notes.has_notes() is False

    def test_transaction_create_with_id(self) -> None:
        """Should create transaction with provided ID."""
        test_id = "transaction-id-123"
        transaction = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
            id=test_id,
        )

        assert transaction.id == test_id

    def test_transaction_id_immutability(self) -> None:
        """Should not be able to change ID after creation."""
        transaction = Transaction(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
            id="test-id-1",
        )

        # ID property should not have a setter
        with pytest.raises(AttributeError):
            transaction.id = "different-id"  # type: ignore[misc]

    def test_transaction_from_persistence(self) -> None:
        """Should create transaction from persistence with existing ID."""
        test_id = "persistence-id-456"
        transaction = Transaction.from_persistence(
            test_id,
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("100.00")),
            transaction_date=date.today(),
        )

        assert transaction.id == test_id
        assert transaction.portfolio_id == "portfolio-id-1"
        assert transaction.stock_id == "stock-id-1"


class TestTransactionType:
    """Test TransactionType value object validation."""

    def test_valid_transaction_types_accepted(self) -> None:
        """Test that valid transaction types are accepted."""
        valid_types = ["buy", "sell"]
        for transaction_type in valid_types:
            trans_type = TransactionType(transaction_type)
            assert trans_type.value == transaction_type

    def test_case_insensitive_transaction_types(self) -> None:
        """Test that transaction types are case insensitive."""
        trans_type1 = TransactionType("BUY")
        trans_type2 = TransactionType("Buy")
        trans_type3 = TransactionType("buy")

        assert trans_type1.value == "buy"
        assert trans_type2.value == "buy"
        assert trans_type3.value == "buy"

    def test_invalid_transaction_types_rejected(self) -> None:
        """Test that invalid transaction types are rejected."""
        invalid_types = ["transfer", "dividend", "split", "", "INVALID"]
        for invalid_type in invalid_types:
            with pytest.raises(ValueError):
                _ = TransactionType(invalid_type)

    def test_transaction_equality_and_hash_with_non_transaction_object(self) -> None:
        """Test that transaction equality and hash work correctly."""

        transaction = Transaction(
            portfolio_id="portfolio-1",
            stock_id="stock-1",
            transaction_date=date(2024, 1, 15),
            transaction_type=TransactionType("buy"),
            price=Money(Decimal("100.00")),
            quantity=Quantity(10),
        )

        # Test equality with different types - should return False (covers line 109)
        assert transaction != "not a transaction"
        assert transaction != 123
        assert transaction != None
        assert transaction != {"portfolio_id": "portfolio-1", "stock_id": "stock-1"}

        # Test hash method for collections usage (covers line 121)
        transaction_hash = hash(transaction)
        assert isinstance(transaction_hash, int)

        # Test that equal transactions have equal hashes
        same_transaction = Transaction(
            portfolio_id="portfolio-1",
            stock_id="stock-1",
            transaction_date=date(2024, 1, 15),
            transaction_type=TransactionType("buy"),
            price=Money(Decimal("100.00")),
            quantity=Quantity(10),
        )
        assert hash(transaction) == hash(same_transaction)
