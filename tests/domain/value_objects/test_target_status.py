"""
Tests for TargetStatus value object.

This module tests the TargetStatus value object which encapsulates
target status validation and business logic for tracking target progress.
"""

from typing import Any

import pytest

from src.domain.value_objects.target_status import TargetStatus


class TestTargetStatusCreation:
    """Test TargetStatus creation and validation."""

    def test_create_active_status(self) -> None:
        """Should create valid active target status."""
        status = TargetStatus("active")

        assert status.value == "active"

    def test_create_hit_status(self) -> None:
        """Should create valid hit target status."""
        status = TargetStatus("hit")

        assert status.value == "hit"

    def test_create_failed_status(self) -> None:
        """Should create valid failed target status."""
        status = TargetStatus("failed")

        assert status.value == "failed"

    def test_create_cancelled_status(self) -> None:
        """Should create valid cancelled target status."""
        status = TargetStatus("cancelled")

        assert status.value == "cancelled"

    def test_create_with_uppercase_normalizes_to_lowercase(self) -> None:
        """Should normalize uppercase values to lowercase."""
        active_upper = TargetStatus("ACTIVE")
        hit_upper = TargetStatus("HIT")
        failed_upper = TargetStatus("FAILED")
        cancelled_upper = TargetStatus("CANCELLED")

        assert active_upper.value == "active"
        assert hit_upper.value == "hit"
        assert failed_upper.value == "failed"
        assert cancelled_upper.value == "cancelled"

    def test_create_with_mixed_case_normalizes_to_lowercase(self) -> None:
        """Should normalize mixed case values to lowercase."""
        active_mixed = TargetStatus("Active")
        hit_mixed = TargetStatus("Hit")
        failed_mixed = TargetStatus("Failed")
        cancelled_mixed = TargetStatus("Cancelled")

        assert active_mixed.value == "active"
        assert hit_mixed.value == "hit"
        assert failed_mixed.value == "failed"
        assert cancelled_mixed.value == "cancelled"

    def test_create_with_whitespace_strips_whitespace(self) -> None:
        """Should strip leading and trailing whitespace."""
        active_whitespace = TargetStatus("  active  ")
        hit_whitespace = TargetStatus("\thit\n")

        assert active_whitespace.value == "active"
        assert hit_whitespace.value == "hit"

    def test_create_with_invalid_status_raises_error(self) -> None:
        """Should raise ValueError for invalid target statuses."""
        invalid_statuses = [
            "invalid",
            "pending",
            "complete",
            "open",
            "closed",
            "paused",
        ]

        for invalid_status in invalid_statuses:
            with pytest.raises(
                ValueError,
                match="Target status must be one of: active, cancelled, failed, hit",
            ):
                TargetStatus(invalid_status)

    def test_create_with_empty_string_raises_error(self) -> None:
        """Should raise ValueError for empty target status."""
        with pytest.raises(
            ValueError,
            match="Target status must be one of: active, cancelled, failed, hit",
        ):
            TargetStatus("")

    def test_create_with_whitespace_only_raises_error(self) -> None:
        """Should raise ValueError for whitespace-only target status."""
        with pytest.raises(
            ValueError,
            match="Target status must be one of: active, cancelled, failed, hit",
        ):
            TargetStatus("   ")

    def test_create_with_partial_match_raises_error(self) -> None:
        """Should raise ValueError for partial matches of valid statuses."""
        partial_matches = ["act", "hi", "fail", "cancel", "activ", "hitt"]

        for partial_match in partial_matches:
            with pytest.raises(
                ValueError,
                match="Target status must be one of: active, cancelled, failed, hit",
            ):
                TargetStatus(partial_match)


class TestTargetStatusEquality:
    """Test TargetStatus equality and hashing."""

    def test_equal_target_statuses_are_equal(self) -> None:
        """Should be equal if target statuses have same value."""
        active1 = TargetStatus("active")
        active2 = TargetStatus("ACTIVE")  # Different case but same normalized value
        hit1 = TargetStatus("hit")
        hit2 = TargetStatus("HIT")

        assert active1 == active2
        assert hit1 == hit2

    def test_different_target_statuses_are_not_equal(self) -> None:
        """Should not be equal if target statuses have different values."""
        active_status = TargetStatus("active")
        hit_status = TargetStatus("hit")
        failed_status = TargetStatus("failed")
        cancelled_status = TargetStatus("cancelled")

        assert active_status != hit_status
        assert active_status != failed_status
        assert active_status != cancelled_status
        assert hit_status != failed_status
        assert hit_status != cancelled_status
        assert failed_status != cancelled_status

    def test_target_status_not_equal_to_other_types(self) -> None:
        """Should not be equal to non-TargetStatus objects."""
        active_status = TargetStatus("active")

        assert active_status != "active"
        assert active_status != 1
        assert active_status != None
        assert active_status != []

    def test_target_status_hashable(self) -> None:
        """Should be hashable for use in collections."""
        active1 = TargetStatus("active")
        active2 = TargetStatus("ACTIVE")
        hit_status = TargetStatus("hit")
        failed_status = TargetStatus("failed")

        # Should be able to use in set
        status_set = {active1, active2, hit_status, failed_status}
        assert len(status_set) == 3  # active1 and active2 should be same hash

        # Should be able to use as dict key
        status_dict = {
            active1: "in progress",
            hit_status: "achieved",
            failed_status: "unsuccessful",
        }
        assert len(status_dict) == 3
        assert status_dict[active2] == "in progress"  # Should find active1's value


class TestTargetStatusImmutability:
    """Test TargetStatus immutability."""

    def test_value_property_is_readonly(self) -> None:
        """Should not be able to modify value after creation."""
        status = TargetStatus("active")

        with pytest.raises(AttributeError):
            status.value = "hit"  # type: ignore[misc]

    def test_cannot_set_attributes_after_creation(self) -> None:
        """Should not be able to set new attributes after creation."""
        status = TargetStatus("active")

        with pytest.raises(AttributeError, match="TargetStatus is immutable"):
            status.new_attribute = "value"  # type: ignore[attr-defined]

    def test_cannot_modify_private_value_attribute(self) -> None:
        """Should not be able to modify private _value attribute."""
        status = TargetStatus("active")

        with pytest.raises(AttributeError, match="TargetStatus is immutable"):
            status._value = "hit"  # type: ignore[misc]


class TestTargetStatusStringRepresentation:
    """Test TargetStatus string representations."""

    def test_str_returns_status_value(self) -> None:
        """Should return target status value as string."""
        active_status = TargetStatus("active")
        hit_status = TargetStatus("hit")
        failed_status = TargetStatus("failed")
        cancelled_status = TargetStatus("cancelled")

        assert str(active_status) == "active"
        assert str(hit_status) == "hit"
        assert str(failed_status) == "failed"
        assert str(cancelled_status) == "cancelled"

    def test_repr_returns_developer_representation(self) -> None:
        """Should return developer-friendly representation."""
        active_status = TargetStatus("active")
        hit_status = TargetStatus("hit")
        failed_status = TargetStatus("failed")
        cancelled_status = TargetStatus("cancelled")

        assert repr(active_status) == "TargetStatus('active')"
        assert repr(hit_status) == "TargetStatus('hit')"
        assert repr(failed_status) == "TargetStatus('failed')"
        assert repr(cancelled_status) == "TargetStatus('cancelled')"


class TestTargetStatusValidStatuses:
    """Test TargetStatus valid statuses constant."""

    def test_valid_statuses_contains_expected_values(self) -> None:
        """Should contain exactly the expected valid statuses."""
        expected_statuses = {"active", "hit", "failed", "cancelled"}
        assert TargetStatus.VALID_STATUSES == expected_statuses

    def test_valid_statuses_is_immutable_set(self) -> None:
        """Should be an immutable set that cannot be modified."""
        valid_statuses = TargetStatus.VALID_STATUSES
        assert isinstance(valid_statuses, set)

        # Verify expected content
        expected_statuses = {"active", "hit", "failed", "cancelled"}
        assert expected_statuses == set(TargetStatus.VALID_STATUSES)


class TestTargetStatusBusinessLogic:
    """Test TargetStatus business logic and state transitions."""

    def test_all_valid_statuses_can_be_created(self) -> None:
        """Should be able to create all valid status types."""
        for status_value in TargetStatus.VALID_STATUSES:
            status = TargetStatus(status_value)
            assert status.value == status_value

    def test_status_lifecycle_progression(self) -> None:
        """Should support typical target lifecycle progression."""
        # Start with active
        active_status = TargetStatus("active")
        assert active_status.value == "active"

        # Can transition to hit (success)
        hit_status = TargetStatus("hit")
        assert hit_status.value == "hit"

        # Or can transition to failed (unsuccessful)
        failed_status = TargetStatus("failed")
        assert failed_status.value == "failed"

        # Or can be cancelled
        cancelled_status = TargetStatus("cancelled")
        assert cancelled_status.value == "cancelled"

    def test_final_states_are_distinguishable(self) -> None:
        """Should be able to distinguish between different final states."""
        hit_status = TargetStatus("hit")
        failed_status = TargetStatus("failed")
        cancelled_status = TargetStatus("cancelled")

        # All different from each other
        assert hit_status != failed_status
        assert hit_status != cancelled_status
        assert failed_status != cancelled_status

        # All different from active
        active_status = TargetStatus("active")
        assert active_status != hit_status
        assert active_status != failed_status
        assert active_status != cancelled_status


class TestTargetStatusEdgeCases:
    """Test TargetStatus edge cases and boundary conditions."""

    def test_create_with_unicode_characters_raises_error(self) -> None:
        """Should raise error for unicode characters in target status."""
        unicode_values = ["activé", "hît", "失败", "キャンセル"]

        for unicode_value in unicode_values:
            with pytest.raises(
                ValueError,
                match="Target status must be one of: active, cancelled, failed, hit",
            ):
                TargetStatus(unicode_value)

    def test_create_with_numeric_strings_raises_error(self) -> None:
        """Should raise error for numeric strings."""
        numeric_values = ["1", "0", "123", "1.5"]

        for numeric_value in numeric_values:
            with pytest.raises(
                ValueError,
                match="Target status must be one of: active, cancelled, failed, hit",
            ):
                TargetStatus(numeric_value)

    def test_create_with_special_characters_raises_error(self) -> None:
        """Should raise error for special characters."""
        special_values = [
            "active!",
            "hit?",
            "failed-status",
            "cancelled/done",
            "active@hit",
        ]

        for special_value in special_values:
            with pytest.raises(
                ValueError,
                match="Target status must be one of: active, cancelled, failed, hit",
            ):
                TargetStatus(special_value)

    def test_create_with_similar_words_raises_error(self) -> None:
        """Should raise error for words similar to valid statuses."""
        similar_words = [
            "activity",
            "hitting",
            "failure",
            "cancellation",
            "activate",
            "hits",
        ]

        for similar_word in similar_words:
            with pytest.raises(
                ValueError,
                match="Target status must be one of: active, cancelled, failed, hit",
            ):
                TargetStatus(similar_word)
