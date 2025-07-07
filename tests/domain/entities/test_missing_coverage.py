"""Tests to cover missing lines in entity constructors."""

import pytest

from src.domain.entities import JournalEntry, PortfolioBalance, Target


class TestEntityConstructorErrors:
    """Test entity constructors that require builder instances."""

    def test_journal_entry_constructor_requires_builder(self) -> None:
        """Test that JournalEntry constructor requires a builder instance."""
        with pytest.raises(
            ValueError,
            match="JournalEntry must be created through Builder",
        ):
            _ = JournalEntry(_builder_instance=None)

    def test_portfolio_balance_constructor_requires_builder(self) -> None:
        """Test that PortfolioBalance constructor requires a builder instance."""
        with pytest.raises(
            ValueError,
            match="PortfolioBalance must be created through Builder",
        ):
            _ = PortfolioBalance(_builder_instance=None)

    def test_target_constructor_requires_builder(self) -> None:
        """Test that Target constructor requires a builder instance."""
        with pytest.raises(ValueError, match="Target must be created through Builder"):
            _ = Target(_builder_instance=None)

    # Transaction already has this test in test_transaction.py
