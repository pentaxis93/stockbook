"""
Tests for Transaction domain entity.

Following TDD approach - these tests define the expected behavior
of the rich Transaction entity with business logic.
"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from src.domain.entities.transaction import Transaction
from src.domain.value_objects import Money, Notes, Quantity
from src.domain.value_objects.transaction_type import TransactionType


class TestTransactionBuilder:
    """Test cases for Transaction.Builder pattern."""

    def test_builder_creates_transaction_with_all_fields(self) -> None:
        """Test that Builder can create a transaction with all fields."""
        transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("150.25")))
            .with_transaction_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_notes(Notes("Initial purchase"))
            .with_id("transaction-id")
            .build()
        )

        assert transaction.portfolio_id == "portfolio-1"
        assert transaction.stock_id == "stock-1"
        assert transaction.transaction_type.value == "buy"
        assert transaction.quantity.value == 100
        assert transaction.price.amount == Decimal("150.25")
        assert transaction.transaction_date == datetime(2024, 1, 15, tzinfo=UTC)
        assert transaction.notes.value == "Initial purchase"
        assert transaction.id == "transaction-id"

    def test_builder_creates_transaction_with_minimal_fields(self) -> None:
        """Test that Builder can create a transaction with only required fields."""
        transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-1")
            .with_transaction_type(TransactionType("sell"))
            .with_quantity(Quantity(50))
            .with_price(Money(Decimal("175.50")))
            .with_transaction_date(datetime(2024, 2, 1, tzinfo=UTC))
            .build()
        )

        assert transaction.portfolio_id == "portfolio-1"
        assert transaction.stock_id == "stock-1"
        assert transaction.transaction_type.value == "sell"
        assert transaction.quantity.value == 50
        assert transaction.price.amount == Decimal("175.50")
        assert transaction.transaction_date == datetime(2024, 2, 1, tzinfo=UTC)
        assert transaction.notes.value == ""  # Default

    def test_builder_raises_error_when_required_fields_missing(self) -> None:
        """Test that Builder raises error when required fields are missing."""
        # Missing portfolio_id
        with pytest.raises(ValueError, match="Portfolio ID is required"):
            _ = (
                Transaction.Builder()
                .with_stock_id("stock-1")
                .with_transaction_type(TransactionType("buy"))
                .with_quantity(Quantity(100))
                .with_price(Money(Decimal("100.00")))
                .with_transaction_date(datetime(2024, 1, 15, tzinfo=UTC))
                .build()
            )

        # Missing stock_id
        with pytest.raises(ValueError, match="Stock ID is required"):
            _ = (
                Transaction.Builder()
                .with_portfolio_id("portfolio-1")
                .with_transaction_type(TransactionType("buy"))
                .with_quantity(Quantity(100))
                .with_price(Money(Decimal("100.00")))
                .with_transaction_date(datetime(2024, 1, 15, tzinfo=UTC))
                .build()
            )

        # Missing transaction_type
        with pytest.raises(ValueError, match="Transaction type is required"):
            _ = (
                Transaction.Builder()
                .with_portfolio_id("portfolio-1")
                .with_stock_id("stock-1")
                .with_quantity(Quantity(100))
                .with_price(Money(Decimal("100.00")))
                .with_transaction_date(datetime(2024, 1, 15, tzinfo=UTC))
                .build()
            )

        # Missing quantity
        with pytest.raises(ValueError, match="Quantity is required"):
            _ = (
                Transaction.Builder()
                .with_portfolio_id("portfolio-1")
                .with_stock_id("stock-1")
                .with_transaction_type(TransactionType("buy"))
                .with_price(Money(Decimal("100.00")))
                .with_transaction_date(datetime(2024, 1, 15, tzinfo=UTC))
                .build()
            )

        # Missing price
        with pytest.raises(ValueError, match="Price is required"):
            _ = (
                Transaction.Builder()
                .with_portfolio_id("portfolio-1")
                .with_stock_id("stock-1")
                .with_transaction_type(TransactionType("buy"))
                .with_quantity(Quantity(100))
                .with_transaction_date(datetime(2024, 1, 15, tzinfo=UTC))
                .build()
            )

        # Missing transaction_date
        with pytest.raises(ValueError, match="Transaction date is required"):
            _ = (
                Transaction.Builder()
                .with_portfolio_id("portfolio-1")
                .with_stock_id("stock-1")
                .with_transaction_type(TransactionType("buy"))
                .with_quantity(Quantity(100))
                .with_price(Money(Decimal("100.00")))
                .build()
            )

    def test_builder_validates_empty_ids(self) -> None:
        """Test that Builder validates empty ID strings."""
        builder = (
            Transaction.Builder()
            .with_stock_id("stock-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime(2024, 1, 15, tzinfo=UTC))
        )

        # Empty portfolio_id should raise error
        with pytest.raises(ValueError, match="Portfolio ID must be a non-empty string"):
            _ = builder.with_portfolio_id("").build()

        # Empty stock_id should raise error
        _ = builder.with_portfolio_id("portfolio-1")
        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            _ = builder.with_stock_id("").build()

    def test_builder_method_chaining(self) -> None:
        """Test that all builder methods return self for chaining."""
        builder = Transaction.Builder()

        assert builder.with_portfolio_id("p1") is builder
        assert builder.with_stock_id("s1") is builder
        assert builder.with_transaction_type(TransactionType("buy")) is builder
        assert builder.with_quantity(Quantity(100)) is builder
        assert builder.with_price(Money(Decimal("100.00"))) is builder
        assert (
            builder.with_transaction_date(datetime(2024, 1, 15, tzinfo=UTC)) is builder
        )
        assert builder.with_notes(Notes("test")) is builder
        assert builder.with_id("id1") is builder

    def test_transaction_constructor_requires_builder(self) -> None:
        """Test that Transaction constructor requires a builder instance."""
        with pytest.raises(
            ValueError, match="Transaction must be created through Builder"
        ):
            _ = Transaction(_builder_instance=None)


class TestTransaction:
    """Test suite for Transaction domain entity."""

    def test_create_transaction_with_value_objects(self) -> None:
        """Should create Transaction entity with value objects only."""
        portfolio_id = "portfolio-1"
        stock_id = "stock-2"
        transaction_type = TransactionType("buy")
        quantity = Quantity(100)
        price = Money(Decimal("150.25"))
        transaction_date = datetime(2024, 1, 15, tzinfo=UTC)
        notes = Notes("Initial purchase")

        transaction = (
            Transaction.Builder()
            .with_portfolio_id(portfolio_id)
            .with_stock_id(stock_id)
            .with_transaction_type(transaction_type)
            .with_quantity(quantity)
            .with_price(price)
            .with_transaction_date(transaction_date)
            .with_notes(notes)
            .build()
        )

        assert transaction.portfolio_id == portfolio_id
        assert transaction.stock_id == stock_id
        assert transaction.transaction_type == transaction_type
        assert transaction.quantity == quantity
        assert transaction.price == price
        assert transaction.transaction_date == transaction_date
        assert transaction.notes == notes
        assert transaction.id is not None  # Generated UUID
        assert isinstance(transaction.id, str)

    def test_create_transaction_with_minimal_data(self) -> None:
        """Should create Transaction with only required fields."""
        portfolio_id = "portfolio-1"
        stock_id = "stock-2"
        transaction_type = TransactionType("sell")
        quantity = Quantity(50)
        price = Money(Decimal("175.50"))
        transaction_date = datetime(2024, 2, 1, tzinfo=UTC)

        transaction = (
            Transaction.Builder()
            .with_portfolio_id(portfolio_id)
            .with_stock_id(stock_id)
            .with_transaction_type(transaction_type)
            .with_quantity(quantity)
            .with_price(price)
            .with_transaction_date(transaction_date)
            .build()
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

        transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(transaction_type)
            .with_quantity(quantity)
            .with_price(price)
            .with_transaction_date(datetime.now(UTC))
            .with_notes(notes)
            .build()
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
        transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime.now(UTC))
            .with_notes(None)
            .build()
        )

        assert transaction.notes.value == ""  # Notes defaults to empty when None

    def test_create_transaction_with_invalid_transaction_type_raises_error(
        self,
    ) -> None:
        """Should raise error for invalid transaction type through TransactionType
        value object."""
        with pytest.raises(
            ValueError, match="Transaction type must be 'buy' or 'sell'"
        ):
            _ = TransactionType(
                "transfer"
            )  # Error happens at TransactionType construction

    def test_create_transaction_with_invalid_portfolio_id_raises_error(self) -> None:
        """Should raise error for invalid portfolio ID."""
        with pytest.raises(ValueError, match="Portfolio ID must be a non-empty string"):
            _ = (
                Transaction.Builder()
                .with_portfolio_id("")
                .with_stock_id("stock-id-1")
                .with_transaction_type(TransactionType("buy"))
                .with_quantity(Quantity(100))
                .with_price(Money(Decimal("100.00")))
                .with_transaction_date(datetime.now(UTC))
                .build()
            )

    def test_create_transaction_with_invalid_stock_id_raises_error(self) -> None:
        """Should raise error for invalid stock ID."""
        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            _ = (
                Transaction.Builder()
                .with_portfolio_id("portfolio-id-1")
                .with_stock_id("")
                .with_transaction_type(TransactionType("buy"))
                .with_quantity(Quantity(100))
                .with_price(Money(Decimal("100.00")))
                .with_transaction_date(datetime.now(UTC))
                .build()
            )

    def test_transaction_equality(self) -> None:
        """Should compare transactions based on ID."""
        transaction1 = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime(2024, 1, 1, tzinfo=UTC))
            .build()
        )

        transaction2 = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime(2024, 1, 1, tzinfo=UTC))
            .build()
        )

        transaction3 = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-2")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime(2024, 1, 1, tzinfo=UTC))
            .build()
        )

        # Different instances with same attributes but different IDs are NOT equal
        assert transaction1 != transaction2  # Different IDs
        assert transaction1 != transaction3  # Different IDs

        # Same ID means equal
        transaction4 = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime(2024, 1, 1, tzinfo=UTC))
            .with_id("same-id")
            .build()
        )
        transaction5 = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-2")
            .with_stock_id("stock-id-2")
            .with_transaction_type(TransactionType("sell"))
            .with_quantity(Quantity(200))
            .with_price(Money(Decimal("200.00")))
            .with_transaction_date(datetime(2024, 2, 1, tzinfo=UTC))
            .with_id("same-id")
            .build()
        )
        assert transaction4 == transaction5  # Same ID, even with different attributes

    def test_transaction_string_representation(self) -> None:
        """Should have meaningful string representation."""
        transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("150.50")))
            .with_transaction_date(datetime(2024, 1, 15, tzinfo=UTC))
            .build()
        )

        expected = "buy 100 @ $150.50 on 2024-01-15 00:00:00+00:00"
        assert str(transaction) == expected

    def test_transaction_repr(self) -> None:
        """Should have detailed repr representation."""
        transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-2")
            .with_transaction_type(TransactionType("sell"))
            .with_quantity(Quantity(50))
            .with_price(Money(Decimal("200.00")))
            .with_transaction_date(datetime(2024, 2, 1, tzinfo=UTC))
            .build()
        )

        expected = (
            "Transaction(portfolio_id=portfolio-id-1, stock_id=stock-id-2, "
            "type='sell', quantity=50, price=$200.00)"
        )
        assert repr(transaction) == expected

    def test_calculate_total_value(self) -> None:
        """Should calculate total transaction value."""
        transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("150.50")))
            .with_transaction_date(datetime.now(UTC))
            .build()
        )

        total_value = transaction.calculate_total_value()

        assert total_value == Money(Decimal("15050.00"))
        assert isinstance(total_value, Money)

    def test_is_buy_transaction(self) -> None:
        """Should check if transaction is a buy."""
        buy_transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime.now(UTC))
            .build()
        )

        sell_transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("sell"))
            .with_quantity(Quantity(50))
            .with_price(Money(Decimal("110.00")))
            .with_transaction_date(datetime.now(UTC))
            .build()
        )

        assert buy_transaction.is_buy() is True
        assert sell_transaction.is_buy() is False

    def test_is_sell_transaction(self) -> None:
        """Should check if transaction is a sell."""
        buy_transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime.now(UTC))
            .build()
        )

        sell_transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("sell"))
            .with_quantity(Quantity(50))
            .with_price(Money(Decimal("110.00")))
            .with_transaction_date(datetime.now(UTC))
            .build()
        )

        assert buy_transaction.is_sell() is False
        assert sell_transaction.is_sell() is True

    def test_has_notes(self) -> None:
        """Should check if transaction has notes."""
        transaction_with_notes = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime.now(UTC))
            .with_notes(Notes("Important transaction"))
            .build()
        )

        transaction_without_notes = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime.now(UTC))
            .build()
        )

        assert transaction_with_notes.has_notes() is True
        assert transaction_without_notes.has_notes() is False

    def test_transaction_create_with_id(self) -> None:
        """Should create transaction with provided ID."""
        test_id = "transaction-id-123"
        transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime.now(UTC))
            .with_id(test_id)
            .build()
        )

        assert transaction.id == test_id

    def test_transaction_id_immutability(self) -> None:
        """Should not be able to change ID after creation."""
        transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime.now(UTC))
            .with_id("test-id-1")
            .build()
        )

        # ID property should not have a setter
        with pytest.raises(AttributeError):
            transaction.id = "different-id"  # type: ignore[misc]

    def test_transaction_from_persistence(self) -> None:
        """Should create transaction from persistence with existing ID."""
        test_id = "persistence-id-456"
        transaction = (
            Transaction.Builder()
            .with_id(test_id)
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-1")
            .with_transaction_type(TransactionType("buy"))
            .with_quantity(Quantity(100))
            .with_price(Money(Decimal("100.00")))
            .with_transaction_date(datetime.now(UTC))
            .build()
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
            with pytest.raises(ValueError, match="Transaction type"):
                _ = TransactionType(invalid_type)

    def test_transaction_equality_and_hash_with_non_transaction_object(self) -> None:
        """Test that transaction equality and hash work correctly."""

        transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-1")
            .with_transaction_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_transaction_type(TransactionType("buy"))
            .with_price(Money(Decimal("100.00")))
            .with_quantity(Quantity(10))
            .build()
        )

        # Test equality with different types - should return False (covers line 109)
        assert transaction != "not a transaction"
        assert transaction != 123
        assert transaction is not None
        assert transaction != {"portfolio_id": "portfolio-1", "stock_id": "stock-1"}

        # Test hash method for collections usage (covers line 121)
        transaction_hash = hash(transaction)
        assert isinstance(transaction_hash, int)

        # Test that transactions with different IDs have different hashes
        # (likely but not guaranteed)
        same_transaction = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-1")
            .with_transaction_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_transaction_type(TransactionType("buy"))
            .with_price(Money(Decimal("100.00")))
            .with_quantity(Quantity(10))
            .build()
        )
        assert hash(transaction) != hash(same_transaction)  # Different IDs

        # Test that transactions with same ID have same hash
        transaction_with_id1 = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-1")
            .with_transaction_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_transaction_type(TransactionType("buy"))
            .with_price(Money(Decimal("100.00")))
            .with_quantity(Quantity(10))
            .with_id("same-id")
            .build()
        )
        transaction_with_id2 = (
            Transaction.Builder()
            .with_portfolio_id("portfolio-2")  # Different attributes
            .with_stock_id("stock-2")
            .with_transaction_date(datetime(2024, 2, 20, tzinfo=UTC))
            .with_transaction_type(TransactionType("sell"))
            .with_price(Money(Decimal("200.00")))
            .with_quantity(Quantity(20))
            .with_id("same-id")
            .build()
        )
        assert hash(transaction_with_id1) == hash(
            transaction_with_id2
        )  # Same ID, same hash
