"""
Tests for Portfolio domain entity.

Following TDD approach - these tests define the expected behavior
of the rich Portfolio entity with business logic.
"""

from datetime import date

import pytest

from src.domain.entities.portfolio_entity import PortfolioEntity
from src.domain.value_objects import Notes
from src.domain.value_objects.portfolio_name import PortfolioName


class TestPortfolioEntity:
    """Test suite for Portfolio domain entity."""

    def test_create_portfolio_with_value_objects(self) -> None:
        """Should create Portfolio entity with value objects only."""
        name = PortfolioName("Growth Portfolio")
        description = Notes("Long-term growth strategy portfolio")
        created_date = date(2024, 1, 1)

        portfolio = PortfolioEntity(
            name=name,
            description=description,
            created_date=created_date,
            is_active=True,
        )

        assert portfolio.name == name
        assert portfolio.description == description
        assert portfolio.created_date == created_date
        assert portfolio.is_active is True
        assert portfolio.id is not None  # Generated nanoid
        assert isinstance(portfolio.id, str)

    def test_create_portfolio_with_minimal_data(self) -> None:
        """Should create Portfolio with only required fields."""
        name = PortfolioName("Simple Portfolio")

        portfolio = PortfolioEntity(name=name)

        assert portfolio.name == name
        assert portfolio.description.value == ""  # Description defaults to empty
        assert portfolio.created_date is None  # Optional
        assert portfolio.is_active is True  # Defaults to True
        assert portfolio.id is not None  # Generated nanoid
        assert isinstance(portfolio.id, str)

    def test_portfolio_stores_value_objects(self) -> None:
        """Should store and return value objects directly."""
        name = PortfolioName("Test Portfolio")
        description = Notes("Test description")

        portfolio = PortfolioEntity(
            name=name,
            description=description,
        )

        # Should return the exact same value objects
        assert portfolio.name is name
        assert portfolio.description is description

        # String access through value property
        assert portfolio.name.value == "Test Portfolio"
        assert portfolio.description.value == "Test description"

    def test_create_portfolio_with_none_description_allowed(self) -> None:
        """Should allow creating portfolio with None for description."""
        portfolio = PortfolioEntity(
            name=PortfolioName("Test Portfolio"),
            description=None,
        )

        assert (
            portfolio.description.value == ""
        )  # Description defaults to empty when None

    def test_create_portfolio_with_invalid_name_raises_error(self) -> None:
        """Should raise error for invalid portfolio name through PortfolioName value object."""
        with pytest.raises(ValueError, match="Portfolio name cannot be empty"):
            PortfolioName("")  # Error happens at PortfolioName construction

    def test_portfolio_equality(self) -> None:
        """Should compare portfolios based on business identity (name)."""
        name1 = PortfolioName("Growth Portfolio")
        name2 = PortfolioName("Growth Portfolio")
        name3 = PortfolioName("Value Portfolio")

        portfolio1 = PortfolioEntity(name=name1)
        portfolio2 = PortfolioEntity(name=name2)  # Same name
        portfolio3 = PortfolioEntity(name=name3)  # Different name

        assert portfolio1 == portfolio2  # Same name
        assert portfolio1 != portfolio3  # Different name

    def test_portfolio_hash(self) -> None:
        """Should be hashable based on name."""
        name1 = PortfolioName("Growth Portfolio")
        name2 = PortfolioName("Growth Portfolio")
        name3 = PortfolioName("Value Portfolio")

        portfolio1 = PortfolioEntity(name=name1)
        portfolio2 = PortfolioEntity(name=name2)
        portfolio3 = PortfolioEntity(name=name3)

        # Same name should have same hash
        assert hash(portfolio1) == hash(portfolio2)

        # Can be used in set
        portfolio_set = {portfolio1, portfolio2, portfolio3}
        assert len(portfolio_set) == 2  # Growth Portfolio appears only once

    def test_portfolio_string_representation(self) -> None:
        """Should have meaningful string representation."""
        name = PortfolioName("Growth Portfolio")
        portfolio = PortfolioEntity(name=name)

        assert str(portfolio) == "Portfolio(Growth Portfolio)"

    def test_portfolio_repr(self) -> None:
        """Should have detailed repr representation."""
        name = PortfolioName("Growth Portfolio")
        portfolio = PortfolioEntity(name=name, is_active=True)

        expected = (
            "PortfolioEntity(name=PortfolioName('Growth Portfolio'), active=True)"
        )
        assert repr(portfolio) == expected

    def test_portfolio_activate(self) -> None:
        """Should be able to activate portfolio."""
        portfolio = PortfolioEntity(
            name=PortfolioName("Test Portfolio"), is_active=False
        )

        portfolio.activate()
        assert portfolio.is_active is True

    def test_portfolio_deactivate(self) -> None:
        """Should be able to deactivate portfolio."""
        portfolio = PortfolioEntity(
            name=PortfolioName("Test Portfolio"), is_active=True
        )

        portfolio.deactivate()
        assert portfolio.is_active is False

    def test_has_description(self) -> None:
        """Should check if portfolio has description."""
        portfolio_with_description = PortfolioEntity(
            name=PortfolioName("Test Portfolio"),
            description=Notes("Important portfolio"),
        )

        portfolio_without_description = PortfolioEntity(
            name=PortfolioName("Test Portfolio"),
        )

        assert portfolio_with_description.has_description() is True
        assert portfolio_without_description.has_description() is False

    def test_update_description(self) -> None:
        """Should allow updating portfolio description."""
        portfolio = PortfolioEntity(
            name=PortfolioName("Test Portfolio"),
        )

        new_description = Notes("Updated description")
        portfolio.update_description(new_description)

        assert portfolio.description == new_description
        assert portfolio.description.value == "Updated description"

    def test_update_description_with_string(self) -> None:
        """Should allow updating description with string (convenience method)."""
        portfolio = PortfolioEntity(
            name=PortfolioName("Test Portfolio"),
        )

        portfolio.update_description("Updated description")

        assert portfolio.description.value == "Updated description"

    def test_create_portfolio_with_id(self) -> None:
        """Should create portfolio with provided ID."""
        test_id = "portfolio-id-123"
        portfolio = PortfolioEntity(name=PortfolioName("Test Portfolio"), id=test_id)

        assert portfolio.id == test_id

    def test_portfolio_id_immutability(self) -> None:
        """Should not be able to change ID after creation."""
        portfolio = PortfolioEntity(
            name=PortfolioName("Test Portfolio"), id="test-id-1"
        )

        # ID property should not have a setter
        with pytest.raises(AttributeError):
            portfolio.id = "different-id"  # type: ignore[misc]

    def test_portfolio_from_persistence(self) -> None:
        """Should create portfolio from persistence with existing ID."""
        test_id = "persistence-id-456"
        portfolio = PortfolioEntity.from_persistence(
            test_id,
            name=PortfolioName("Test Portfolio"),
            description=Notes("From database"),
            is_active=False,
        )

        assert portfolio.id == test_id
        assert portfolio.name.value == "Test Portfolio"
        assert portfolio.is_active is False

    def test_is_active_portfolio(self) -> None:
        """Should check if portfolio is active."""
        active_portfolio = PortfolioEntity(
            name=PortfolioName("Active Portfolio"), is_active=True
        )

        inactive_portfolio = PortfolioEntity(
            name=PortfolioName("Inactive Portfolio"), is_active=False
        )

        assert active_portfolio.is_active_portfolio() is True
        assert inactive_portfolio.is_active_portfolio() is False

    def test_set_created_date(self) -> None:
        """Should allow setting created date."""
        portfolio = PortfolioEntity(name=PortfolioName("Test Portfolio"))

        creation_date = date(2024, 1, 15)
        portfolio.set_created_date(creation_date)

        assert portfolio.created_date == creation_date

    def test_set_created_date_when_already_set_raises_error(self) -> None:
        """Should raise error when trying to change existing created date."""
        portfolio = PortfolioEntity(
            name=PortfolioName("Test Portfolio"), created_date=date(2024, 1, 1)
        )

        with pytest.raises(
            ValueError, match="Created date is already set and cannot be changed"
        ):
            portfolio.set_created_date(date(2024, 1, 15))


class TestPortfolioName:
    """Test PortfolioName value object validation."""

    def test_valid_portfolio_names_accepted(self) -> None:
        """Test that valid portfolio names are accepted."""
        valid_names = [
            "Growth Portfolio",
            "A",
            "Value Investing Strategy",
            "Portfolio #1",
        ]
        for name in valid_names:
            portfolio_name = PortfolioName(name)
            assert portfolio_name.value == name

    def test_portfolio_name_strips_whitespace(self) -> None:
        """Test that portfolio names are stripped of leading/trailing whitespace."""
        name = PortfolioName("  Growth Portfolio  ")
        assert name.value == "Growth Portfolio"

    def test_empty_portfolio_names_rejected(self) -> None:
        """Test that empty portfolio names are rejected."""
        empty_names = ["", "   ", "\t", "\n"]
        for empty_name in empty_names:
            with pytest.raises(ValueError, match="Portfolio name cannot be empty"):
                PortfolioName(empty_name)

    def test_too_long_portfolio_names_rejected(self) -> None:
        """Test that excessively long portfolio names are rejected."""
        long_name = "A" * 101  # Max is 100 characters
        with pytest.raises(
            ValueError, match="Portfolio name cannot exceed 100 characters"
        ):
            PortfolioName(long_name)

    def test_max_length_portfolio_name_accepted(self) -> None:
        """Test that portfolio name at max length is accepted."""
        max_length_name = "A" * 100  # Exactly 100 characters
        portfolio_name = PortfolioName(max_length_name)
        assert portfolio_name.value == max_length_name
        assert len(portfolio_name.value) == 100
