"""
Tests for BaseEntity domain entity.

Following TDD approach - these tests define the expected behavior
of the BaseEntity with focus on ID management and equality behavior.
"""

import pytest

from src.domain.entities.base import BaseEntity


class ConcreteEntity(BaseEntity):
    """Concrete implementation of BaseEntity for testing."""

    def __init__(self, name: str = "test", entity_id: str = None) -> None:
        super().__init__(entity_id=entity_id)
        self.name = name


class TestBaseEntity:
    """Test suite for BaseEntity domain entity."""

    def test_create_entity_without_id(self):
        """Should create entity with generated nanoid by default."""
        entity = ConcreteEntity()
        assert entity.id is not None
        assert isinstance(entity.id, str)
        assert len(entity.id) > 0

    def test_create_entity_with_provided_id(self):
        """Should create entity with provided string ID."""
        test_id = "test-id-123"
        entity = ConcreteEntity(entity_id=test_id)
        assert entity.id == test_id

    def test_id_is_immutable(self):
        """Should not be able to change ID after creation."""
        entity = ConcreteEntity(entity_id="test-id-1")
        # The ID property should not have a setter
        with pytest.raises(AttributeError):
            entity.id = "different-id"

    def test_from_persistence_creates_entity_with_id(self):
        """Should create entity from persistence with existing ID."""
        test_id = "persistence-id-456"
        entity = ConcreteEntity.from_persistence(test_id, name="from_db")
        assert entity.id == test_id
        assert entity.name == "from_db"

    def test_equality_with_same_id_same_type(self):
        """Should be equal when same type and same ID."""
        test_id = "same-id-789"
        entity1 = ConcreteEntity("first", entity_id=test_id)
        entity2 = ConcreteEntity("second", entity_id=test_id)
        assert entity1 == entity2

    def test_equality_with_different_ids(self):
        """Should not be equal when different IDs."""
        entity1 = ConcreteEntity(entity_id="id-1")
        entity2 = ConcreteEntity(entity_id="id-2")
        assert entity1 != entity2

    def test_equality_with_generated_ids(self):
        """Should not be equal when both have generated IDs."""
        entity1 = ConcreteEntity()
        entity2 = ConcreteEntity()
        assert entity1 != entity2

    def test_equality_with_different_types(self):
        """Should not be equal when different types."""

        class AnotherEntity(BaseEntity):
            pass

        test_id = "same-id-123"
        entity1 = ConcreteEntity(entity_id=test_id)
        entity2 = AnotherEntity(entity_id=test_id)
        assert entity1 != entity2

    def test_equality_with_non_entity_object(self):
        """Should not be equal to non-entity objects."""
        entity = ConcreteEntity(entity_id="test-id-1")
        assert entity != "not an entity"
        assert entity != "test-id-1"

    def test_entities_not_hashable(self):
        """Should not be hashable after removing __hash__ method."""
        entity = ConcreteEntity(entity_id="test-id-1")

        # Entities should not be usable as dict keys
        with pytest.raises(TypeError, match="unhashable type"):
            {entity: "value"}

        # Entities should not be usable in sets
        with pytest.raises(TypeError, match="unhashable type"):
            {entity}

    def test_str_representation_with_id(self):
        """Should display class name and ID in string representation."""
        test_id = "test-id-42"
        entity = ConcreteEntity(entity_id=test_id)
        assert str(entity) == f"ConcreteEntity(id={test_id})"

    def test_repr_same_as_str(self):
        """Should have same repr as str representation."""
        entity = ConcreteEntity(entity_id="test-id-1")
        assert repr(entity) == str(entity)


class TestBaseEntityArchitecturalConcerns:
    """
    Test suite focusing on architectural concerns about BaseEntity design.

    These tests highlight design decisions:
    1. String IDs with nanoid provide immutable, unique identifiers
    2. from_persistence() method handles entity reconstruction from database
    3. __hash__() method removal prevents misuse of mutable entities
    """

    def test_id_immutability_design_improvement(self):
        """
        DESIGN IMPROVEMENT: IDs are now immutable by design.

        The new implementation eliminates the set_id() method that caused
        architectural concerns. IDs are set during construction and cannot
        be changed, which better aligns with DDD principles.

        BENEFITS:
        - No public ID mutation methods
        - IDs are set once during entity creation
        - from_persistence() method handles database reconstruction
        - Immutable IDs prevent accidental changes
        """
        # IDs are generated automatically
        entity = ConcreteEntity()
        original_id = entity.id
        assert original_id is not None
        assert isinstance(original_id, str)

        # IDs cannot be changed after creation
        with pytest.raises(AttributeError):
            entity.id = "different-id"

        # ID remains unchanged
        assert entity.id == original_id

    def test_from_persistence_handles_database_reconstruction(self):
        """
        DESIGN SOLUTION: from_persistence() handles database entity creation.

        This class method provides a clean way for the infrastructure layer
        to create entities with known IDs from database records, without
        exposing ID mutation in the domain layer.
        """
        db_id = "db-entity-id-123"
        entity = ConcreteEntity.from_persistence(db_id, name="from_database")

        assert entity.id == db_id
        assert entity.name == "from_database"

        # The entity works exactly like any other entity
        other_entity = ConcreteEntity("other", entity_id=db_id)
        assert entity == other_entity

    def test_nanoid_provides_unique_identifiers(self):
        """
        DESIGN DECISION: nanoid generates unique string identifiers.

        Using nanoid eliminates the need for database-generated integer IDs
        in many scenarios, allowing entities to have IDs before persistence.
        """
        entities = [ConcreteEntity() for _ in range(100)]
        ids = [entity.id for entity in entities]

        # All IDs should be unique
        assert len(set(ids)) == len(ids)

        # All IDs should be non-empty strings
        assert all(isinstance(id, str) and len(id) > 0 for id in ids)

    def test_hash_removal_prevents_misuse(self):
        """
        DESIGN IMPROVEMENT: Removing __hash__() prevents misuse.

        By removing __hash__(), we prevent mutable entities from being
        used as dictionary keys or in sets, which violates Python's
        hash contract for mutable objects.
        """
        entity = ConcreteEntity("test", entity_id="test-id-1")

        # Entities can no longer be misused as dict keys
        with pytest.raises(TypeError, match="unhashable type"):
            {entity: "value"}

        # Entities can no longer be misused in sets
        with pytest.raises(TypeError, match="unhashable type"):
            {entity}

        # But equality still works fine for proper comparisons
        other_entity = ConcreteEntity("other", entity_id="test-id-1")
        assert entity == other_entity

    def test_entity_collections_work_properly_without_hash(self):
        """
        Test how entities work in collections without __hash__().

        Shows that entities can still be compared for equality and used in lists,
        but are prevented from being misused in hash-based collections.
        """
        test_id = "collection-test-id"
        entity1 = ConcreteEntity(entity_id=test_id)
        entity2 = ConcreteEntity(entity_id=test_id)

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
