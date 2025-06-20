"""
Tests for diversification metrics value objects.

Following TDD approach - these tests define the expected behavior
for immutable value objects that represent diversification analysis results.
"""

from decimal import Decimal
from typing import Dict

import pytest

from src.domain.services.value_objects.diversification_metrics import (
    CorrelationMatrix,
    DiversificationScore,
    SectorAllocation,
)
from src.domain.value_objects import Money


class TestSectorAllocation:
    """Test suite for SectorAllocation value object."""

    def test_create_sector_allocation_with_valid_data(self):
        """Should create SectorAllocation with valid allocations and total value."""
        allocations = {
            "Technology": Decimal("0.40"),
            "Healthcare": Decimal("0.30"),
            "Financial": Decimal("0.30"),
        }
        total_value = Money(Decimal("10000.00"), "USD")

        sector_allocation = SectorAllocation(
            allocations=allocations, total_value=total_value
        )

        assert sector_allocation.allocations == allocations
        assert sector_allocation.total_value == total_value

    def test_create_sector_allocation_with_empty_allocations(self):
        """Should create SectorAllocation with empty allocations."""
        allocations = {}
        total_value = Money(Decimal("0.00"), "USD")

        sector_allocation = SectorAllocation(
            allocations=allocations, total_value=total_value
        )

        assert sector_allocation.allocations == {}
        assert sector_allocation.total_value == total_value

    def test_get_sector_percentage_existing_sector(self):
        """Should return correct percentage for existing sector."""
        allocations = {
            "Technology": Decimal("0.40"),
            "Healthcare": Decimal("0.30"),
            "Financial": Decimal("0.30"),
        }
        total_value = Money(Decimal("10000.00"), "USD")

        sector_allocation = SectorAllocation(
            allocations=allocations, total_value=total_value
        )

        assert sector_allocation.get_sector_percentage("Technology") == Decimal("0.40")
        assert sector_allocation.get_sector_percentage("Healthcare") == Decimal("0.30")
        assert sector_allocation.get_sector_percentage("Financial") == Decimal("0.30")

    def test_get_sector_percentage_non_existing_sector(self):
        """Should return zero for non-existing sector."""
        allocations = {"Technology": Decimal("0.50")}
        total_value = Money(Decimal("5000.00"), "USD")

        sector_allocation = SectorAllocation(
            allocations=allocations, total_value=total_value
        )

        assert sector_allocation.get_sector_percentage("Energy") == Decimal("0")
        assert sector_allocation.get_sector_percentage("Utilities") == Decimal("0")

    def test_get_sector_percentage_empty_allocations(self):
        """Should return zero for any sector when allocations are empty."""
        allocations = {}
        total_value = Money(Decimal("0.00"), "USD")

        sector_allocation = SectorAllocation(
            allocations=allocations, total_value=total_value
        )

        assert sector_allocation.get_sector_percentage("Technology") == Decimal("0")
        assert sector_allocation.get_sector_percentage("Healthcare") == Decimal("0")

    def test_sector_allocation_is_immutable(self):
        """SectorAllocation should be immutable (frozen dataclass)."""
        allocations = {"Technology": Decimal("0.50")}
        total_value = Money(Decimal("5000.00"), "USD")

        sector_allocation = SectorAllocation(
            allocations=allocations, total_value=total_value
        )

        # Attempting to modify should raise AttributeError
        with pytest.raises(AttributeError):
            sector_allocation.allocations = {}

        with pytest.raises(AttributeError):
            sector_allocation.total_value = Money(Decimal("0.00"), "USD")

    def test_sector_allocation_equality(self):
        """Should compare SectorAllocation objects for equality."""
        allocations = {"Technology": Decimal("0.50")}
        total_value = Money(Decimal("5000.00"), "USD")

        allocation1 = SectorAllocation(allocations=allocations, total_value=total_value)
        allocation2 = SectorAllocation(allocations=allocations, total_value=total_value)
        allocation3 = SectorAllocation(
            allocations={"Healthcare": Decimal("0.50")}, total_value=total_value
        )

        assert allocation1 == allocation2
        assert allocation1 != allocation3

    def test_sector_allocation_hash(self):
        """Should handle hashability appropriately (dictionaries are not hashable)."""
        allocations = {"Technology": Decimal("0.50")}
        total_value = Money(Decimal("5000.00"), "USD")

        allocation1 = SectorAllocation(allocations=allocations, total_value=total_value)

        # Dataclass with dict field is not hashable by default
        with pytest.raises(TypeError, match="unhashable type"):
            hash(allocation1)

        # Cannot be used in set due to unhashable dict
        with pytest.raises(TypeError, match="unhashable type"):
            _ = {allocation1}

    def test_sector_allocation_with_decimal_precision(self):
        """Should handle decimal precision correctly."""
        allocations = {
            "Technology": Decimal("0.333333"),
            "Healthcare": Decimal("0.333333"),
            "Financial": Decimal("0.333334"),  # Adds to 1.0
        }
        total_value = Money(Decimal("9999.99"), "USD")

        sector_allocation = SectorAllocation(
            allocations=allocations, total_value=total_value
        )

        assert sector_allocation.get_sector_percentage("Technology") == Decimal(
            "0.333333"
        )
        assert sector_allocation.get_sector_percentage("Healthcare") == Decimal(
            "0.333333"
        )
        assert sector_allocation.get_sector_percentage("Financial") == Decimal(
            "0.333334"
        )


class TestCorrelationMatrix:
    """Test suite for CorrelationMatrix value object."""

    def test_create_correlation_matrix_with_valid_data(self):
        """Should create CorrelationMatrix with valid correlation data."""
        correlations = {
            ("AAPL", "MSFT"): Decimal("0.75"),
            ("AAPL", "GOOGL"): Decimal("0.68"),
            ("MSFT", "GOOGL"): Decimal("0.82"),
        }

        matrix = CorrelationMatrix(correlations=correlations)

        assert matrix.correlations == correlations

    def test_create_correlation_matrix_with_empty_data(self):
        """Should create CorrelationMatrix with empty correlation data."""
        correlations = {}

        matrix = CorrelationMatrix(correlations=correlations)

        assert matrix.correlations == {}

    def test_get_correlation_forward_key(self):
        """Should return correlation for forward key (symbol1, symbol2)."""
        correlations = {
            ("AAPL", "MSFT"): Decimal("0.75"),
            ("AAPL", "GOOGL"): Decimal("0.68"),
            ("MSFT", "GOOGL"): Decimal("0.82"),
        }

        matrix = CorrelationMatrix(correlations=correlations)

        assert matrix.get_correlation("AAPL", "MSFT") == Decimal("0.75")
        assert matrix.get_correlation("AAPL", "GOOGL") == Decimal("0.68")
        assert matrix.get_correlation("MSFT", "GOOGL") == Decimal("0.82")

    def test_get_correlation_reverse_key(self):
        """Should return correlation for reverse key (symbol2, symbol1)."""
        correlations = {
            ("AAPL", "MSFT"): Decimal("0.75"),
            ("AAPL", "GOOGL"): Decimal("0.68"),
            ("MSFT", "GOOGL"): Decimal("0.82"),
        }

        matrix = CorrelationMatrix(correlations=correlations)

        # Should work in reverse order
        assert matrix.get_correlation("MSFT", "AAPL") == Decimal("0.75")
        assert matrix.get_correlation("GOOGL", "AAPL") == Decimal("0.68")
        assert matrix.get_correlation("GOOGL", "MSFT") == Decimal("0.82")

    def test_get_correlation_non_existing_pair(self):
        """Should return zero for non-existing correlation pair."""
        correlations = {("AAPL", "MSFT"): Decimal("0.75")}

        matrix = CorrelationMatrix(correlations=correlations)

        assert matrix.get_correlation("AAPL", "TSLA") == Decimal("0")
        assert matrix.get_correlation("TSLA", "AAPL") == Decimal("0")
        assert matrix.get_correlation("TSLA", "MSFT") == Decimal("0")

    def test_get_correlation_empty_matrix(self):
        """Should return zero for any pair when matrix is empty."""
        correlations = {}

        matrix = CorrelationMatrix(correlations=correlations)

        assert matrix.get_correlation("AAPL", "MSFT") == Decimal("0")
        assert matrix.get_correlation("MSFT", "AAPL") == Decimal("0")

    def test_get_correlation_same_symbol(self):
        """Should return zero when asking for correlation of symbol with itself."""
        correlations = {("AAPL", "MSFT"): Decimal("0.75")}

        matrix = CorrelationMatrix(correlations=correlations)

        # Self-correlation should return 0 since it's not stored
        assert matrix.get_correlation("AAPL", "AAPL") == Decimal("0")
        assert matrix.get_correlation("MSFT", "MSFT") == Decimal("0")

    def test_correlation_matrix_is_immutable(self):
        """CorrelationMatrix should be immutable (frozen dataclass)."""
        correlations = {("AAPL", "MSFT"): Decimal("0.75")}

        matrix = CorrelationMatrix(correlations=correlations)

        # Attempting to modify should raise AttributeError
        with pytest.raises(AttributeError):
            matrix.correlations = {}

    def test_correlation_matrix_equality(self):
        """Should compare CorrelationMatrix objects for equality."""
        correlations = {("AAPL", "MSFT"): Decimal("0.75")}

        matrix1 = CorrelationMatrix(correlations=correlations)
        matrix2 = CorrelationMatrix(correlations=correlations)
        matrix3 = CorrelationMatrix(correlations={("AAPL", "GOOGL"): Decimal("0.68")})

        assert matrix1 == matrix2
        assert matrix1 != matrix3

    def test_correlation_matrix_hash(self):
        """Should handle hashability appropriately (dictionaries are not hashable)."""
        correlations = {("AAPL", "MSFT"): Decimal("0.75")}

        matrix1 = CorrelationMatrix(correlations=correlations)

        # Dataclass with dict field is not hashable by default
        with pytest.raises(TypeError, match="unhashable type"):
            hash(matrix1)

        # Cannot be used in set due to unhashable dict
        with pytest.raises(TypeError, match="unhashable type"):
            _ = {matrix1}

    def test_correlation_matrix_with_negative_correlations(self):
        """Should handle negative correlation values correctly."""
        correlations = {
            ("AAPL", "BOND"): Decimal("-0.25"),
            ("TECH", "GOLD"): Decimal("-0.45"),
        }

        matrix = CorrelationMatrix(correlations=correlations)

        assert matrix.get_correlation("AAPL", "BOND") == Decimal("-0.25")
        assert matrix.get_correlation("BOND", "AAPL") == Decimal("-0.25")
        assert matrix.get_correlation("TECH", "GOLD") == Decimal("-0.45")
        assert matrix.get_correlation("GOLD", "TECH") == Decimal("-0.45")

    def test_correlation_matrix_with_extreme_values(self):
        """Should handle extreme correlation values (1.0, -1.0)."""
        correlations = {
            ("PERFECT_POS", "CLONE"): Decimal("1.0"),
            ("PERFECT_NEG", "OPPOSITE"): Decimal("-1.0"),
        }

        matrix = CorrelationMatrix(correlations=correlations)

        assert matrix.get_correlation("PERFECT_POS", "CLONE") == Decimal("1.0")
        assert matrix.get_correlation("PERFECT_NEG", "OPPOSITE") == Decimal("-1.0")


class TestDiversificationScore:
    """Test suite for DiversificationScore value object."""

    def test_create_diversification_score_with_all_scores(self):
        """Should create DiversificationScore with all score components."""
        score = DiversificationScore(
            overall_score=Decimal("0.75"),
            sector_score=Decimal("0.80"),
            market_cap_score=Decimal("0.70"),
            correlation_score=Decimal("0.85"),
            geographic_score=Decimal("0.65"),
        )

        assert score.overall_score == Decimal("0.75")
        assert score.sector_score == Decimal("0.80")
        assert score.market_cap_score == Decimal("0.70")
        assert score.correlation_score == Decimal("0.85")
        assert score.geographic_score == Decimal("0.65")

    def test_create_diversification_score_without_geographic_score(self):
        """Should create DiversificationScore without geographic score (optional)."""
        score = DiversificationScore(
            overall_score=Decimal("0.75"),
            sector_score=Decimal("0.80"),
            market_cap_score=Decimal("0.70"),
            correlation_score=Decimal("0.85"),
        )

        assert score.overall_score == Decimal("0.75")
        assert score.sector_score == Decimal("0.80")
        assert score.market_cap_score == Decimal("0.70")
        assert score.correlation_score == Decimal("0.85")
        assert score.geographic_score is None

    def test_letter_grade_a_plus(self):
        """Should return A+ for scores >= 0.9."""
        score = DiversificationScore(
            overall_score=Decimal("0.95"),
            sector_score=Decimal("0.90"),
            market_cap_score=Decimal("0.90"),
            correlation_score=Decimal("0.90"),
        )

        assert score.letter_grade == "A+"

        # Test boundary
        score_boundary = DiversificationScore(
            overall_score=Decimal("0.90"),
            sector_score=Decimal("0.90"),
            market_cap_score=Decimal("0.90"),
            correlation_score=Decimal("0.90"),
        )

        assert score_boundary.letter_grade == "A+"

    def test_letter_grade_a(self):
        """Should return A for scores >= 0.8 and < 0.9."""
        score = DiversificationScore(
            overall_score=Decimal("0.85"),
            sector_score=Decimal("0.80"),
            market_cap_score=Decimal("0.80"),
            correlation_score=Decimal("0.80"),
        )

        assert score.letter_grade == "A"

        # Test boundary
        score_boundary = DiversificationScore(
            overall_score=Decimal("0.80"),
            sector_score=Decimal("0.80"),
            market_cap_score=Decimal("0.80"),
            correlation_score=Decimal("0.80"),
        )

        assert score_boundary.letter_grade == "A"

    def test_letter_grade_b_plus(self):
        """Should return B+ for scores >= 0.7 and < 0.8."""
        score = DiversificationScore(
            overall_score=Decimal("0.75"),
            sector_score=Decimal("0.70"),
            market_cap_score=Decimal("0.70"),
            correlation_score=Decimal("0.70"),
        )

        assert score.letter_grade == "B+"

        # Test boundary
        score_boundary = DiversificationScore(
            overall_score=Decimal("0.70"),
            sector_score=Decimal("0.70"),
            market_cap_score=Decimal("0.70"),
            correlation_score=Decimal("0.70"),
        )

        assert score_boundary.letter_grade == "B+"

    def test_letter_grade_b(self):
        """Should return B for scores >= 0.6 and < 0.7."""
        score = DiversificationScore(
            overall_score=Decimal("0.65"),
            sector_score=Decimal("0.60"),
            market_cap_score=Decimal("0.60"),
            correlation_score=Decimal("0.60"),
        )

        assert score.letter_grade == "B"

        # Test boundary
        score_boundary = DiversificationScore(
            overall_score=Decimal("0.60"),
            sector_score=Decimal("0.60"),
            market_cap_score=Decimal("0.60"),
            correlation_score=Decimal("0.60"),
        )

        assert score_boundary.letter_grade == "B"

    def test_letter_grade_c_plus(self):
        """Should return C+ for scores >= 0.5 and < 0.6."""
        score = DiversificationScore(
            overall_score=Decimal("0.55"),
            sector_score=Decimal("0.50"),
            market_cap_score=Decimal("0.50"),
            correlation_score=Decimal("0.50"),
        )

        assert score.letter_grade == "C+"

        # Test boundary
        score_boundary = DiversificationScore(
            overall_score=Decimal("0.50"),
            sector_score=Decimal("0.50"),
            market_cap_score=Decimal("0.50"),
            correlation_score=Decimal("0.50"),
        )

        assert score_boundary.letter_grade == "C+"

    def test_letter_grade_c(self):
        """Should return C for scores >= 0.4 and < 0.5."""
        score = DiversificationScore(
            overall_score=Decimal("0.45"),
            sector_score=Decimal("0.40"),
            market_cap_score=Decimal("0.40"),
            correlation_score=Decimal("0.40"),
        )

        assert score.letter_grade == "C"

        # Test boundary
        score_boundary = DiversificationScore(
            overall_score=Decimal("0.40"),
            sector_score=Decimal("0.40"),
            market_cap_score=Decimal("0.40"),
            correlation_score=Decimal("0.40"),
        )

        assert score_boundary.letter_grade == "C"

    def test_letter_grade_d(self):
        """Should return D for scores < 0.4."""
        score = DiversificationScore(
            overall_score=Decimal("0.35"),
            sector_score=Decimal("0.30"),
            market_cap_score=Decimal("0.30"),
            correlation_score=Decimal("0.30"),
        )

        assert score.letter_grade == "D"

        # Test very low score
        score_low = DiversificationScore(
            overall_score=Decimal("0.10"),
            sector_score=Decimal("0.10"),
            market_cap_score=Decimal("0.10"),
            correlation_score=Decimal("0.10"),
        )

        assert score_low.letter_grade == "D"

        # Test zero score
        score_zero = DiversificationScore(
            overall_score=Decimal("0.00"),
            sector_score=Decimal("0.00"),
            market_cap_score=Decimal("0.00"),
            correlation_score=Decimal("0.00"),
        )

        assert score_zero.letter_grade == "D"

    def test_diversification_score_is_immutable(self):
        """DiversificationScore should be immutable (frozen dataclass)."""
        score = DiversificationScore(
            overall_score=Decimal("0.75"),
            sector_score=Decimal("0.80"),
            market_cap_score=Decimal("0.70"),
            correlation_score=Decimal("0.85"),
        )

        # Attempting to modify should raise AttributeError
        with pytest.raises(AttributeError):
            score.overall_score = Decimal("0.50")

        with pytest.raises(AttributeError):
            score.sector_score = Decimal("0.50")

        with pytest.raises(AttributeError):
            score.geographic_score = Decimal("0.50")

    def test_diversification_score_equality(self):
        """Should compare DiversificationScore objects for equality."""
        score1 = DiversificationScore(
            overall_score=Decimal("0.75"),
            sector_score=Decimal("0.80"),
            market_cap_score=Decimal("0.70"),
            correlation_score=Decimal("0.85"),
        )
        score2 = DiversificationScore(
            overall_score=Decimal("0.75"),
            sector_score=Decimal("0.80"),
            market_cap_score=Decimal("0.70"),
            correlation_score=Decimal("0.85"),
        )
        score3 = DiversificationScore(
            overall_score=Decimal("0.60"),
            sector_score=Decimal("0.80"),
            market_cap_score=Decimal("0.70"),
            correlation_score=Decimal("0.85"),
        )

        assert score1 == score2
        assert score1 != score3

    def test_diversification_score_hash(self):
        """Should be hashable for use in sets/dicts."""
        score1 = DiversificationScore(
            overall_score=Decimal("0.75"),
            sector_score=Decimal("0.80"),
            market_cap_score=Decimal("0.70"),
            correlation_score=Decimal("0.85"),
        )
        score2 = DiversificationScore(
            overall_score=Decimal("0.75"),
            sector_score=Decimal("0.80"),
            market_cap_score=Decimal("0.70"),
            correlation_score=Decimal("0.85"),
        )

        # Same scores should have same hash
        assert hash(score1) == hash(score2)

        # Can be used in set
        score_set = {score1, score2}
        assert len(score_set) == 1

    def test_diversification_score_with_perfect_scores(self):
        """Should handle perfect diversification scores correctly."""
        perfect_score = DiversificationScore(
            overall_score=Decimal("1.0"),
            sector_score=Decimal("1.0"),
            market_cap_score=Decimal("1.0"),
            correlation_score=Decimal("1.0"),
            geographic_score=Decimal("1.0"),
        )

        assert perfect_score.letter_grade == "A+"
        assert perfect_score.geographic_score == Decimal("1.0")

    def test_diversification_score_with_zero_scores(self):
        """Should handle zero diversification scores correctly."""
        zero_score = DiversificationScore(
            overall_score=Decimal("0.0"),
            sector_score=Decimal("0.0"),
            market_cap_score=Decimal("0.0"),
            correlation_score=Decimal("0.0"),
            geographic_score=Decimal("0.0"),
        )

        assert zero_score.letter_grade == "D"
        assert zero_score.geographic_score == Decimal("0.0")

    def test_diversification_score_boundary_conditions(self):
        """Should handle boundary conditions correctly for letter grading."""
        # Test just below A+ threshold
        score_below_a_plus = DiversificationScore(
            overall_score=Decimal("0.899"),
            sector_score=Decimal("0.80"),
            market_cap_score=Decimal("0.70"),
            correlation_score=Decimal("0.85"),
        )
        assert score_below_a_plus.letter_grade == "A"

        # Test just below A threshold
        score_below_a = DiversificationScore(
            overall_score=Decimal("0.799"),
            sector_score=Decimal("0.80"),
            market_cap_score=Decimal("0.70"),
            correlation_score=Decimal("0.85"),
        )
        assert score_below_a.letter_grade == "B+"

        # Test just above D threshold
        score_above_d = DiversificationScore(
            overall_score=Decimal("0.400"),
            sector_score=Decimal("0.40"),
            market_cap_score=Decimal("0.40"),
            correlation_score=Decimal("0.40"),
        )
        assert score_above_d.letter_grade == "C"

        # Test just below C threshold
        score_below_c = DiversificationScore(
            overall_score=Decimal("0.399"),
            sector_score=Decimal("0.30"),
            market_cap_score=Decimal("0.30"),
            correlation_score=Decimal("0.30"),
        )
        assert score_below_c.letter_grade == "D"
