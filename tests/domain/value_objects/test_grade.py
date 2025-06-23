"""
Test suite for Grade value object.
"""

import pytest

from src.domain.value_objects.grade import Grade


class TestGradeValueObject:
    """Test cases for Grade value object."""

    def test_grade_creation_with_valid_value(self) -> None:
        """Test creating grade with valid values A, B, C, D, F."""
        for valid_grade in ["A", "B", "C", "D", "F"]:
            grade = Grade(valid_grade)
            assert grade.value == valid_grade
            assert str(grade) == valid_grade

    def test_grade_creation_strips_whitespace(self) -> None:
        """Test grade creation strips leading/trailing whitespace."""
        grade = Grade("  A  ")
        assert grade.value == "A"

    def test_grade_creation_normalizes_case(self) -> None:
        """Test grade creation normalizes to uppercase."""
        grade = Grade("a")
        assert grade.value == "A"

        grade = Grade("b")
        assert grade.value == "B"

        grade = Grade("d")
        assert grade.value == "D"

        grade = Grade("f")
        assert grade.value == "F"

    def test_grade_creation_with_invalid_value_raises_error(self) -> None:
        """Test grade creation with invalid values raises ValueError."""
        invalid_grades = ["E", "G", "1", "AA", "Z", "X"]
        for invalid_grade in invalid_grades:
            with pytest.raises(ValueError, match="Grade must be one of"):
                _ = Grade(invalid_grade)

    def test_grade_creation_with_empty_string_raises_error(self) -> None:
        """Test grade creation with empty string raises ValueError."""
        with pytest.raises(ValueError, match="Grade cannot be empty"):
            _ = Grade("")

    def test_grade_creation_with_whitespace_only_raises_error(self) -> None:
        """Test grade creation with whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Grade cannot be empty"):
            _ = Grade("   ")

    def test_grade_equality(self) -> None:
        """Test grade equality comparison."""
        grade1 = Grade("A")
        grade2 = Grade("A")
        grade3 = Grade("B")

        assert grade1 == grade2
        assert grade1 != grade3
        assert grade2 != grade3

    def test_grade_equality_with_case_insensitive_input(self) -> None:
        """Test grade equality works with case insensitive input."""
        grade1 = Grade("A")
        grade2 = Grade("a")
        assert grade1 == grade2

    def test_grade_equality_with_different_types(self) -> None:
        """Test grade equality with non-Grade objects."""
        grade = Grade("A")
        assert grade != "A"
        assert grade != 123
        assert grade is not None

    def test_grade_hash(self) -> None:
        """Test grade can be used as dictionary key."""
        grade1 = Grade("A")
        grade2 = Grade("A")
        grade3 = Grade("B")

        # Same value should have same hash
        assert hash(grade1) == hash(grade2)

        # Can be used in set
        grade_set = {grade1, grade2, grade3}
        assert len(grade_set) == 2  # grade1 and grade2 are duplicates

    def test_grade_repr(self) -> None:
        """Test grade developer representation."""
        grade = Grade("A")
        assert repr(grade) == "Grade('A')"

    def test_grade_immutability(self) -> None:
        """Test grade cannot be modified after creation."""
        grade = Grade("A")

        with pytest.raises(AttributeError, match="Grade is immutable"):
            grade.value = "B"  # type: ignore[misc] - Testing immutability

        with pytest.raises(AttributeError, match="Grade is immutable"):
            grade._value = "B"  # type: ignore[attr-defined]

    def test_grade_equality_with_non_grade_object(self) -> None:
        """Test that grade equality returns False for non-Grade objects."""
        grade = Grade("A")

        # Test equality with different types - should return False
        assert grade != "A"
        assert grade != 123
        assert grade != None
        assert grade != {"value": "A"}

    def test_grade_valid_grades_constant(self) -> None:
        """Test that VALID_GRADES constant is accessible and correct."""
        assert Grade.VALID_GRADES == {"A", "B", "C", "D", "F"}

    def test_grade_base_class_coverage(self) -> None:
        """Test base class coverage for Grade missing lines."""
        # Test that normal initialization works (covers line 71 - super().__setattr__)
        grade = Grade("A")
        assert grade.value == "A"
