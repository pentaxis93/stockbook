"""
Tests for BaseEntity domain entity.

Following TDD approach - these tests define the expected behavior
of the BaseEntity with focus on ID management and equality behavior.
"""

import pytest

from src.domain.entities.base import BaseEntity


class ConcreteEntity(BaseEntity):
    """Concrete implementation of BaseEntity for testing."""

    def __init__(self, name: str = "test") -> None:
        super().__init__()
        self.name = name


class TestBaseEntity:
    """Test suite for BaseEntity domain entity."""

    def test_create_entity_without_id(self):
        """Should create entity with None ID by default."""
        entity = ConcreteEntity()
        assert entity.id is None

    def test_set_id_with_valid_positive_integer(self):
        """Should set ID with valid positive integer."""
        entity = ConcreteEntity()
        entity.set_id(1)
        assert entity.id == 1

    def test_set_id_with_zero_raises_error(self):
        """Should raise ValueError when setting ID to zero."""
        entity = ConcreteEntity()
        with pytest.raises(ValueError, match="ID must be a positive integer"):
            entity.set_id(0)

    def test_set_id_with_negative_raises_error(self):
        """Should raise ValueError when setting negative ID."""
        entity = ConcreteEntity()
        with pytest.raises(ValueError, match="ID must be a positive integer"):
            entity.set_id(-1)

    def test_set_id_with_non_integer_raises_error(self):
        """Should raise ValueError when setting non-integer ID."""
        entity = ConcreteEntity()
        with pytest.raises(ValueError, match="ID must be a positive integer"):
            entity.set_id("1")  # type: ignore

    def test_set_id_twice_raises_error(self):
        """Should raise ValueError when trying to set ID twice."""
        entity = ConcreteEntity()
        entity.set_id(1)
        with pytest.raises(ValueError, match="ID is already set and cannot be changed"):
            entity.set_id(2)

    def test_equality_with_same_id_same_type(self):
        """Should be equal when same type and same ID."""
        entity1 = ConcreteEntity("first")
        entity2 = ConcreteEntity("second")
        entity1.set_id(1)
        entity2.set_id(1)
        assert entity1 == entity2

    def test_equality_with_different_ids(self):
        """Should not be equal when different IDs."""
        entity1 = ConcreteEntity()
        entity2 = ConcreteEntity()
        entity1.set_id(1)
        entity2.set_id(2)
        assert entity1 != entity2

    def test_equality_with_none_ids(self):
        """Should not be equal when both IDs are None."""
        entity1 = ConcreteEntity()
        entity2 = ConcreteEntity()
        assert entity1 != entity2

    def test_equality_with_one_none_id(self):
        """Should not be equal when one ID is None."""
        entity1 = ConcreteEntity()
        entity2 = ConcreteEntity()
        entity1.set_id(1)
        assert entity1 != entity2

    def test_equality_with_different_types(self):
        """Should not be equal when different types."""

        class AnotherEntity(BaseEntity):
            pass

        entity1 = ConcreteEntity()
        entity2 = AnotherEntity()
        entity1.set_id(1)
        entity2.set_id(1)
        assert entity1 != entity2

    def test_equality_with_non_entity_object(self):
        """Should not be equal to non-entity objects."""
        entity = ConcreteEntity()
        entity.set_id(1)
        assert entity != "not an entity"
        assert entity != 1

    def test_entities_not_hashable(self):
        """Should not be hashable after removing __hash__ method."""
        entity = ConcreteEntity()
        entity.set_id(1)

        # Entities should not be usable as dict keys
        with pytest.raises(TypeError, match="unhashable type"):
            {entity: "value"}

        # Entities should not be usable in sets
        with pytest.raises(TypeError, match="unhashable type"):
            {entity}

    def test_str_representation_with_id(self):
        """Should display class name and ID in string representation."""
        entity = ConcreteEntity()
        entity.set_id(42)
        assert str(entity) == "ConcreteEntity(id=42)"

    def test_str_representation_without_id(self):
        """Should display class name and None ID in string representation."""
        entity = ConcreteEntity()
        assert str(entity) == "ConcreteEntity(id=None)"

    def test_repr_same_as_str(self):
        """Should have same repr as str representation."""
        entity = ConcreteEntity()
        entity.set_id(1)
        assert repr(entity) == str(entity)


class TestBaseEntityArchitecturalConcerns:
    """
    Test suite focusing on architectural concerns about BaseEntity design.

    These tests highlight design questions:
    1. Is set_id() needed if IDs are managed by the database?
    2. Is __hash__() method necessary for domain entities?
    """

    def test_set_id_design_concern_database_managed_ids(self):
        """
        DESIGN CONCERN: Should set_id() exist if database manages IDs?

        In DDD, entities typically don't manage their own persistence IDs.
        The database/ORM typically assigns IDs during persistence.
        This test demonstrates the concern about exposing set_id() publicly.

        CURRENT USAGE: set_id() is widely used in:
        - Entity constructors (when loading from database)
        - Infrastructure layer (after database persistence)
        - Application services (when retrieving entities)

        ALTERNATIVE APPROACH: Use private _set_id() method that only
        the persistence layer can access, keeping ID management
        out of the domain layer's public API.
        """
        entity = ConcreteEntity()

        # This works, but should it be allowed in domain layer?
        entity.set_id(1)
        assert entity.id == 1

        # The concern: Domain entities shouldn't manage persistence details
        # The reality: Current architecture requires this for entity hydration
        # TODO: Consider refactoring to use factory pattern or private method

    def test_hash_removal_prevents_misuse(self):
        """
        DESIGN IMPROVEMENT: Removing __hash__() prevents misuse.

        By removing __hash__(), we prevent mutable entities from being
        used as dictionary keys or in sets, which violates Python's
        hash contract for mutable objects.
        """
        entity = ConcreteEntity("test")
        entity.set_id(1)

        # Entities can no longer be misused as dict keys
        with pytest.raises(TypeError, match="unhashable type"):
            {entity: "value"}

        # Entities can no longer be misused in sets
        with pytest.raises(TypeError, match="unhashable type"):
            {entity}

        # But equality still works fine for proper comparisons
        other_entity = ConcreteEntity("other")
        other_entity.set_id(1)
        assert entity == other_entity

    def test_entity_collections_work_properly_without_hash(self):
        """
        Test how entities work in collections without __hash__().

        Shows that entities can still be compared for equality and used in lists,
        but are prevented from being misused in hash-based collections.
        """
        entity1 = ConcreteEntity()
        entity2 = ConcreteEntity()
        entity1.set_id(1)
        entity2.set_id(1)

        # Equality works fine without hash
        assert entity1 == entity2

        # Lists work fine without hash
        entity_list = [entity1, entity2]
        assert len(entity_list) == 2

        # Sets and dict keys are prevented (which is good for mutable entities)
        with pytest.raises(TypeError, match="unhashable type"):
            {entity1, entity2}

        with pytest.raises(TypeError, match="unhashable type"):
            {entity1: "value"}
