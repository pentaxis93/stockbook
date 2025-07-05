"""
Tests for Entity domain entity.

Following TDD approach - these tests define the expected behavior
of the Entity with focus on ID management and equality behavior.
"""

from abc import ABC

import pytest

from src.domain.entities.entity import Entity


class ConcreteEntity(Entity):
    """Concrete implementation of Entity for testing."""

    def __init__(self, name: str = "test", id: str | None = None) -> None:
        super().__init__(id=id)
        self.name = name


class TestEntity:
    """Test suite for Entity domain entity."""

    def test_entity_is_abstract_base_class(self) -> None:
        """Entity should be an ABC and not instantiable directly."""
        # Entity should inherit from ABC
        assert issubclass(Entity, ABC)

        # Should not be able to instantiate Entity directly
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            Entity()  # type: ignore

    def test_create_entity_without_id(self) -> None:
        """Should create entity with generated UUID by default."""
        entity = ConcreteEntity()
        assert entity.id is not None
        assert isinstance(entity.id, str)
        assert len(entity.id) > 0

    def test_create_entity_with_provided_id(self) -> None:
        """Should create entity with provided string ID."""
        test_id = "test-id-123"
        entity = ConcreteEntity(id=test_id)
        assert entity.id == test_id

    def test_id_is_immutable(self) -> None:
        """Should not be able to change ID after creation."""
        entity = ConcreteEntity(id="test-id-1")
        # The ID property should not have a setter
        with pytest.raises(AttributeError):
            entity.id = "different-id"  # type: ignore[misc]

    def test_from_persistence_creates_entity_with_id(self) -> None:
        """Should create entity from persistence with existing ID."""
        test_id = "persistence-id-456"
        entity = ConcreteEntity.from_persistence(test_id, name="from_db")
        assert entity.id == test_id
        assert entity.name == "from_db"

    def test_equality_with_same_id_same_type(self) -> None:
        """Should be equal when same type and same ID."""
        test_id = "same-id-789"
        entity1 = ConcreteEntity("first", id=test_id)
        entity2 = ConcreteEntity("second", id=test_id)
        assert entity1 == entity2

    def test_equality_with_different_ids(self) -> None:
        """Should not be equal when different IDs."""
        entity1 = ConcreteEntity(id="id-1")
        entity2 = ConcreteEntity(id="id-2")
        assert entity1 != entity2

    def test_equality_with_generated_ids(self) -> None:
        """Should not be equal when both have generated IDs."""
        entity1 = ConcreteEntity()
        entity2 = ConcreteEntity()
        assert entity1 != entity2

    def test_equality_with_different_types(self) -> None:
        """Should not be equal when different types."""

        class AnotherEntity(Entity):
            pass

        test_id = "same-id-123"
        entity1 = ConcreteEntity(id=test_id)
        entity2 = AnotherEntity(id=test_id)
        assert entity1 != entity2

    def test_equality_with_non_entity_object(self) -> None:
        """Should not be equal to non-entity objects."""
        entity = ConcreteEntity(id="test-id-1")
        assert entity != "not an entity"
        assert entity != "test-id-1"

    def test_entities_are_hashable(self) -> None:
        """Entities should be hashable based on their ID."""
        entity1 = ConcreteEntity(id="test-id-1")
        entity2 = ConcreteEntity(id="test-id-2")
        entity3 = ConcreteEntity(id="test-id-1")

        # Entities can be used as dict keys
        d = {entity1: "value1", entity2: "value2"}
        assert d[entity1] == "value1"
        assert d[entity2] == "value2"

        # Entities with same ID have same hash
        assert hash(entity1) == hash(entity3)

        # Entities with different IDs have different hashes (likely but not guaranteed)
        assert hash(entity1) != hash(entity2)

        # Entities can be used in sets
        s = {entity1, entity2, entity3}
        assert len(s) == 2  # entity1 and entity3 are considered the same

    def test_str_representation_with_id(self) -> None:
        """Should display class name and ID in string representation."""
        test_id = "test-id-42"
        entity = ConcreteEntity(id=test_id)
        assert str(entity) == f"ConcreteEntity(id={test_id})"

    def test_repr_shows_all_public_attributes(self) -> None:
        """Repr should show class name, ID, and all public attributes."""
        test_id = "test-repr-id"
        entity = ConcreteEntity(name="test-name", id=test_id)

        repr_str = repr(entity)

        # Should contain class name
        assert "ConcreteEntity" in repr_str

        # Should contain ID
        assert f"id='{test_id}'" in repr_str

        # Should contain other attributes
        assert "name='test-name'" in repr_str

        # Should be properly formatted
        assert repr_str.startswith("ConcreteEntity(")
        assert repr_str.endswith(")")

    def test_repr_excludes_private_attributes(self) -> None:
        """Repr should not include private attributes."""
        entity = ConcreteEntity(id="private-test")
        # Use object.__setattr__ to bypass attribute setting restrictions
        object.__setattr__(entity, "_private_attr", "should-not-appear")

        repr_str = repr(entity)

        assert "_private_attr" not in repr_str
        assert "should-not-appear" not in repr_str


class TestEntityArchitecturalConcerns:
    """
    Test suite focusing on architectural concerns about Entity design.

    These tests highlight design decisions:
    1. String IDs with UUID provide immutable, unique identifiers
    2. from_persistence() method handles entity reconstruction from database
    3. __hash__() method removal prevents misuse of mutable entities
    """

    def test_id_immutability_design_improvement(self) -> None:
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
            entity.id = "different-id"  # type: ignore[misc]

        # ID remains unchanged
        assert entity.id == original_id

    def test_from_persistence_handles_database_reconstruction(self) -> None:
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
        other_entity = ConcreteEntity("other", id=db_id)
        assert entity == other_entity

    def test_uuid_provides_unique_identifiers(self) -> None:
        """
        DESIGN DECISION: UUID generates unique string identifiers.

        Using UUID eliminates the need for database-generated integer IDs
        in many scenarios, allowing entities to have IDs before persistence.
        """
        entities = [ConcreteEntity() for _ in range(100)]
        ids = [entity.id for entity in entities]

        # All IDs should be unique
        assert len(set(ids)) == len(ids)

        # All IDs should be non-empty strings
        assert all(isinstance(id, str) and len(id) > 0 for id in ids)

    def test_hash_based_on_id(self) -> None:
        """
        DESIGN DECISION: Hash based on immutable ID.

        Entities are hashed based on their ID, which is immutable.
        This allows entities to be used in sets and as dict keys
        safely, as the hash value will not change during the entity's lifetime.
        """
        entity = ConcreteEntity("test", id="test-id-1")

        # Entities can be used as dict keys
        d = {entity: "value"}
        assert d[entity] == "value"

        # Entities can be used in sets
        s = {entity}
        assert entity in s

        # Equality still works based on ID
        other_entity = ConcreteEntity("other", id="test-id-1")
        assert entity == other_entity
        assert hash(entity) == hash(other_entity)

    def test_from_persistence_type_safety(self) -> None:
        """from_persistence should return the correct subclass type."""
        # Type checker should recognize this returns ConcreteEntity
        entity = ConcreteEntity.from_persistence("test-id", name="typed")
        assert isinstance(entity, ConcreteEntity)
        assert entity.name == "typed"  # Should have access to ConcreteEntity attributes

        # The returned type should be recognized as ConcreteEntity by type checkers
        # This is a compile-time check but we verify runtime behavior here

    def test_entity_collections_work_properly_with_hash(self) -> None:
        """
        Test how entities work in collections with ID-based __hash__().

        Shows that entities can be used in all collection types with proper
        ID-based equality and hashing behavior.
        """
        test_id = "collection-test-id"
        entity1 = ConcreteEntity(id=test_id)
        entity2 = ConcreteEntity(id=test_id)
        entity3 = ConcreteEntity(id="different-id")

        # Equality works based on ID
        assert entity1 == entity2
        assert entity1 != entity3

        # Lists work normally
        entity_list = [entity1, entity2, entity3]
        assert len(entity_list) == 3

        # Sets deduplicate based on ID
        entity_set = {entity1, entity2, entity3}
        assert len(entity_set) == 2  # entity1 and entity2 are considered the same

        # Entities can be used as dict keys
        entity_dict = {entity1: "value1", entity3: "value3"}
        assert entity_dict[entity2] == "value1"  # entity2 is same as entity1
        assert len(entity_dict) == 2
