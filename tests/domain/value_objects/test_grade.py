"""
Test suite for Grade value object.
"""

import pytest

from domain.value_objects.grade import Grade


class TestGradeValueObject:
    """Test cases for Grade value object."""

    def test_grade_creation_with_valid_value(self):
        """Test creating grade with valid values A, B, C, D, F."""
        for valid_grade in ["A", "B", "C", "D", "F"]:
            grade = Grade(valid_grade)
            assert grade.value == valid_grade
            assert str(grade) == valid_grade

    def test_grade_creation_strips_whitespace(self):
        """Test grade creation strips leading/trailing whitespace."""
        grade = Grade("  A  ")
        assert grade.value == "A"

    def test_grade_creation_normalizes_case(self):
        """Test grade creation normalizes to uppercase."""
        grade = Grade("a")
        assert grade.value == "A"

        grade = Grade("b")
        assert grade.value == "B"

        grade = Grade("d")
        assert grade.value == "D"

        grade = Grade("f")
        assert grade.value == "F"

    def test_grade_creation_with_invalid_value_raises_error(self):
        """Test grade creation with invalid values raises ValueError."""
        invalid_grades = ["E", "G", "1", "AA", "Z", "X"]
        for invalid_grade in invalid_grades:
            with pytest.raises(ValueError, match="Grade must be one of"):
                Grade(invalid_grade)

    def test_grade_creation_with_empty_string_raises_error(self):
        """Test grade creation with empty string raises ValueError."""
        with pytest.raises(ValueError, match="Grade cannot be empty"):
            Grade("")

    def test_grade_creation_with_whitespace_only_raises_error(self):
        """Test grade creation with whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Grade cannot be empty"):
            Grade("   ")

    def test_grade_equality(self):
        """Test grade equality comparison."""
        grade1 = Grade("A")
        grade2 = Grade("A")
        grade3 = Grade("B")

        assert grade1 == grade2
        assert grade1 != grade3
        assert grade2 != grade3

    def test_grade_equality_with_case_insensitive_input(self):
        """Test grade equality works with case insensitive input."""
        grade1 = Grade("A")
        grade2 = Grade("a")
        assert grade1 == grade2

    def test_grade_equality_with_different_types(self):
        """Test grade equality with non-Grade objects."""
        grade = Grade("A")
        assert grade != "A"
        assert grade != 123
        assert grade != None

    def test_grade_hash(self):
        """Test grade can be used as dictionary key."""
        grade1 = Grade("A")
        grade2 = Grade("A")
        grade3 = Grade("B")

        # Same value should have same hash
        assert hash(grade1) == hash(grade2)

        # Can be used in set
        grade_set = {grade1, grade2, grade3}
        assert len(grade_set) == 2  # grade1 and grade2 are duplicates

    def test_grade_repr(self):
        """Test grade developer representation."""
        grade = Grade("A")
        assert repr(grade) == "Grade('A')"

    def test_grade_immutability(self):
        """Test grade cannot be modified after creation."""
        grade = Grade("A")

        with pytest.raises(AttributeError, match="Grade is immutable"):
            grade.value = "B"

        with pytest.raises(AttributeError, match="Grade is immutable"):
            grade._value = "B"

    def test_grade_valid_grades_constant(self):
        """Test that VALID_GRADES constant is accessible and correct."""
        assert Grade.VALID_GRADES == {"A", "B", "C", "D", "F"}
