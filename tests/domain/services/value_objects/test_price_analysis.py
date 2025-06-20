"""
Tests for price analysis value objects.

Following TDD approach - these tests define the expected behavior
for immutable value objects that represent price analysis results.
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest

from src.domain.services.value_objects.price_analysis import (
    AlertType,
    PriceAlert,
    PriceAnalysis,
    PriceTrend,
    TrendDirection,
)
from src.domain.value_objects.money import Money
from src.domain.value_objects.stock_symbol import StockSymbol


class TestTrendDirection:
    """Test suite for TrendDirection enum."""

    def test_trend_direction_enum_values(self):
        """Should have correct enum values for trend directions."""
        assert TrendDirection.UPWARD.value == "upward"
        assert TrendDirection.DOWNWARD.value == "downward"
        assert TrendDirection.SIDEWAYS.value == "sideways"

    def test_trend_direction_enum_comparison(self):
        """Should compare enum values correctly."""
        assert TrendDirection.UPWARD == TrendDirection.UPWARD
        assert TrendDirection.UPWARD != TrendDirection.DOWNWARD
        assert TrendDirection.DOWNWARD != TrendDirection.SIDEWAYS

    def test_trend_direction_enum_membership(self):
        """Should be able to check membership in enum."""
        assert TrendDirection.UPWARD in TrendDirection
        assert TrendDirection.DOWNWARD in TrendDirection
        assert TrendDirection.SIDEWAYS in TrendDirection

    def test_trend_direction_enum_string_representation(self):
        """Should have proper string representation."""
        assert str(TrendDirection.UPWARD) == "TrendDirection.UPWARD"
        assert repr(TrendDirection.UPWARD) == "<TrendDirection.UPWARD: 'upward'>"

    def test_trend_direction_enum_iteration(self):
        """Should be able to iterate over enum values."""
        directions = list(TrendDirection)
        assert len(directions) == 3
        assert TrendDirection.UPWARD in directions
        assert TrendDirection.DOWNWARD in directions
        assert TrendDirection.SIDEWAYS in directions


class TestAlertType:
    """Test suite for AlertType enum."""

    def test_alert_type_enum_values(self):
        """Should have correct enum values for alert types."""
        assert AlertType.PRICE_THRESHOLD.value == "price_threshold"
        assert AlertType.PERCENTAGE_CHANGE.value == "percentage_change"
        assert AlertType.HIGH_VOLATILITY.value == "high_volatility"
        assert AlertType.TECHNICAL_INDICATOR.value == "technical_indicator"

    def test_alert_type_enum_comparison(self):
        """Should compare enum values correctly."""
        assert AlertType.PRICE_THRESHOLD == AlertType.PRICE_THRESHOLD
        assert AlertType.PRICE_THRESHOLD != AlertType.PERCENTAGE_CHANGE
        assert AlertType.HIGH_VOLATILITY != AlertType.TECHNICAL_INDICATOR

    def test_alert_type_enum_membership(self):
        """Should be able to check membership in enum."""
        assert AlertType.PRICE_THRESHOLD in AlertType
        assert AlertType.PERCENTAGE_CHANGE in AlertType
        assert AlertType.HIGH_VOLATILITY in AlertType
        assert AlertType.TECHNICAL_INDICATOR in AlertType

    def test_alert_type_enum_string_representation(self):
        """Should have proper string representation."""
        assert str(AlertType.PRICE_THRESHOLD) == "AlertType.PRICE_THRESHOLD"
        assert (
            repr(AlertType.PRICE_THRESHOLD)
            == "<AlertType.PRICE_THRESHOLD: 'price_threshold'>"
        )

    def test_alert_type_enum_iteration(self):
        """Should be able to iterate over enum values."""
        alert_types = list(AlertType)
        assert len(alert_types) == 4
        assert AlertType.PRICE_THRESHOLD in alert_types
        assert AlertType.PERCENTAGE_CHANGE in alert_types
        assert AlertType.HIGH_VOLATILITY in alert_types
        assert AlertType.TECHNICAL_INDICATOR in alert_types


class TestPriceTrend:
    """Test suite for PriceTrend value object."""

    def test_create_price_trend_with_valid_data(self):
        """Should create PriceTrend with valid trend data."""
        trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.8"),
            duration_days=30,
            confidence_level=Decimal("0.85"),
        )

        assert trend.direction == TrendDirection.UPWARD
        assert trend.strength == Decimal("0.8")
        assert trend.duration_days == 30
        assert trend.confidence_level == Decimal("0.85")

    def test_create_price_trend_with_different_directions(self):
        """Should create PriceTrend with different trend directions."""
        upward_trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.7"),
            duration_days=15,
            confidence_level=Decimal("0.8"),
        )

        downward_trend = PriceTrend(
            direction=TrendDirection.DOWNWARD,
            strength=Decimal("0.6"),
            duration_days=20,
            confidence_level=Decimal("0.75"),
        )

        sideways_trend = PriceTrend(
            direction=TrendDirection.SIDEWAYS,
            strength=Decimal("0.3"),
            duration_days=45,
            confidence_level=Decimal("0.9"),
        )

        assert upward_trend.direction == TrendDirection.UPWARD
        assert downward_trend.direction == TrendDirection.DOWNWARD
        assert sideways_trend.direction == TrendDirection.SIDEWAYS

    def test_is_strong_trend_with_high_strength_and_confidence(self):
        """Should identify strong trend when both strength and confidence are high."""
        strong_trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.8"),
            duration_days=30,
            confidence_level=Decimal("0.9"),
        )

        assert strong_trend.is_strong_trend is True

    def test_is_strong_trend_at_boundary_values(self):
        """Should identify strong trend at exact boundary values."""
        boundary_trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.7"),  # Exactly at threshold
            duration_days=30,
            confidence_level=Decimal("0.8"),  # Exactly at threshold
        )

        assert boundary_trend.is_strong_trend is True

    def test_is_strong_trend_with_low_strength(self):
        """Should not identify as strong trend when strength is below threshold."""
        weak_strength_trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.6"),  # Below 0.7 threshold
            duration_days=30,
            confidence_level=Decimal("0.9"),
        )

        assert weak_strength_trend.is_strong_trend is False

    def test_is_strong_trend_with_low_confidence(self):
        """Should not identify as strong trend when confidence is below threshold."""
        low_confidence_trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.8"),
            duration_days=30,
            confidence_level=Decimal("0.7"),  # Below 0.8 threshold
        )

        assert low_confidence_trend.is_strong_trend is False

    def test_is_strong_trend_with_both_below_threshold(self):
        """Should not identify as strong trend when both metrics are below threshold."""
        weak_trend = PriceTrend(
            direction=TrendDirection.SIDEWAYS,
            strength=Decimal("0.5"),
            duration_days=10,
            confidence_level=Decimal("0.6"),
        )

        assert weak_trend.is_strong_trend is False

    def test_price_trend_is_immutable(self):
        """PriceTrend should be immutable (frozen dataclass)."""
        trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.8"),
            duration_days=30,
            confidence_level=Decimal("0.85"),
        )

        # Attempting to modify should raise AttributeError
        with pytest.raises(AttributeError):
            trend.direction = TrendDirection.DOWNWARD

        with pytest.raises(AttributeError):
            trend.strength = Decimal("0.5")

        with pytest.raises(AttributeError):
            trend.duration_days = 60

        with pytest.raises(AttributeError):
            trend.confidence_level = Decimal("0.9")

    def test_price_trend_equality(self):
        """Should compare PriceTrend objects for equality."""
        trend1 = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.8"),
            duration_days=30,
            confidence_level=Decimal("0.85"),
        )
        trend2 = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.8"),
            duration_days=30,
            confidence_level=Decimal("0.85"),
        )
        trend3 = PriceTrend(
            direction=TrendDirection.DOWNWARD,
            strength=Decimal("0.8"),
            duration_days=30,
            confidence_level=Decimal("0.85"),
        )

        assert trend1 == trend2
        assert trend1 != trend3

    def test_price_trend_hash(self):
        """Should be hashable for use in sets/dicts."""
        trend1 = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.8"),
            duration_days=30,
            confidence_level=Decimal("0.85"),
        )
        trend2 = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.8"),
            duration_days=30,
            confidence_level=Decimal("0.85"),
        )

        # Same trends should have same hash
        assert hash(trend1) == hash(trend2)

        # Can be used in set
        trend_set = {trend1, trend2}
        assert len(trend_set) == 1

    def test_price_trend_with_extreme_values(self):
        """Should handle extreme values correctly."""
        # Maximum values
        max_trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("1.0"),
            duration_days=365,
            confidence_level=Decimal("1.0"),
        )

        # Minimum values
        min_trend = PriceTrend(
            direction=TrendDirection.SIDEWAYS,
            strength=Decimal("0.0"),
            duration_days=1,
            confidence_level=Decimal("0.0"),
        )

        assert max_trend.is_strong_trend is True
        assert min_trend.is_strong_trend is False

    def test_price_trend_with_decimal_precision(self):
        """Should handle decimal precision correctly."""
        precise_trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.7500000"),
            duration_days=30,
            confidence_level=Decimal("0.8500000"),
        )

        assert precise_trend.strength == Decimal("0.7500000")
        assert precise_trend.confidence_level == Decimal("0.8500000")
        assert precise_trend.is_strong_trend is True


class TestPriceAlert:
    """Test suite for PriceAlert value object."""

    def test_create_price_alert_with_required_fields(self):
        """Should create PriceAlert with required fields."""
        symbol = StockSymbol("AAPL")
        current_price = Money(Decimal("150.00"))

        alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.PRICE_THRESHOLD,
            message="Price above $150",
            current_price=current_price,
        )

        assert alert.symbol == symbol
        assert alert.alert_type == AlertType.PRICE_THRESHOLD
        assert alert.message == "Price above $150"
        assert alert.current_price == current_price
        assert alert.trigger_value is None
        assert alert.timestamp is not None
        assert alert.severity == "medium"

    def test_create_price_alert_with_all_fields(self):
        """Should create PriceAlert with all fields specified."""
        symbol = StockSymbol("MSFT")
        current_price = Money(Decimal("300.00"))
        trigger_value = Money(Decimal("295.00"))
        timestamp = datetime(2023, 6, 15, 10, 30, 0)

        alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.PERCENTAGE_CHANGE,
            message="Price increased by 5%",
            current_price=current_price,
            trigger_value=trigger_value,
            timestamp=timestamp,
            severity="high",
        )

        assert alert.symbol == symbol
        assert alert.alert_type == AlertType.PERCENTAGE_CHANGE
        assert alert.message == "Price increased by 5%"
        assert alert.current_price == current_price
        assert alert.trigger_value == trigger_value
        assert alert.timestamp == timestamp
        assert alert.severity == "high"

    def test_create_price_alert_with_different_alert_types(self):
        """Should create PriceAlert with different alert types."""
        symbol = StockSymbol("GOOGL")
        current_price = Money(Decimal("120.00"))

        threshold_alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.PRICE_THRESHOLD,
            message="Price threshold alert",
            current_price=current_price,
        )

        volatility_alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.HIGH_VOLATILITY,
            message="High volatility detected",
            current_price=current_price,
        )

        technical_alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.TECHNICAL_INDICATOR,
            message="RSI oversold",
            current_price=current_price,
        )

        assert threshold_alert.alert_type == AlertType.PRICE_THRESHOLD
        assert volatility_alert.alert_type == AlertType.HIGH_VOLATILITY
        assert technical_alert.alert_type == AlertType.TECHNICAL_INDICATOR

    def test_create_price_alert_with_different_severities(self):
        """Should create PriceAlert with different severity levels."""
        symbol = StockSymbol("TSLA")
        current_price = Money(Decimal("200.00"))

        low_alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.PRICE_THRESHOLD,
            message="Low severity alert",
            current_price=current_price,
            severity="low",
        )

        high_alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.HIGH_VOLATILITY,
            message="High severity alert",
            current_price=current_price,
            severity="high",
        )

        assert low_alert.severity == "low"
        assert high_alert.severity == "high"

    @patch("src.domain.services.value_objects.price_analysis.datetime")
    def test_price_alert_auto_timestamp(self, mock_datetime):
        """Should automatically set timestamp when not provided."""
        fixed_datetime = datetime(2023, 6, 15, 14, 30, 0)
        mock_datetime.now.return_value = fixed_datetime

        symbol = StockSymbol("NVDA")
        current_price = Money(Decimal("400.00"))

        alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.PRICE_THRESHOLD,
            message="Auto timestamp test",
            current_price=current_price,
        )

        # __post_init__ should call datetime.now()
        mock_datetime.now.assert_called_once()
        assert alert.timestamp == fixed_datetime

    def test_price_alert_explicit_timestamp_not_overridden(self):
        """Should not override explicitly provided timestamp."""
        symbol = StockSymbol("AMD")
        current_price = Money(Decimal("100.00"))
        explicit_timestamp = datetime(2023, 5, 10, 9, 15, 0)

        alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.PERCENTAGE_CHANGE,
            message="Explicit timestamp test",
            current_price=current_price,
            timestamp=explicit_timestamp,
        )

        assert alert.timestamp == explicit_timestamp

    def test_price_alert_is_immutable(self):
        """PriceAlert should be immutable (frozen dataclass)."""
        symbol = StockSymbol("INTC")
        current_price = Money(Decimal("50.00"))

        alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.TECHNICAL_INDICATOR,
            message="Immutability test",
            current_price=current_price,
        )

        # Attempting to modify should raise AttributeError
        with pytest.raises(AttributeError):
            alert.symbol = StockSymbol("AMD")

        with pytest.raises(AttributeError):
            alert.alert_type = AlertType.HIGH_VOLATILITY

        with pytest.raises(AttributeError):
            alert.message = "Modified message"

        with pytest.raises(AttributeError):
            alert.current_price = Money(Decimal("60.00"))

    def test_price_alert_equality(self):
        """Should compare PriceAlert objects for equality."""
        symbol = StockSymbol("ORCL")
        current_price = Money(Decimal("80.00"))
        timestamp = datetime(2023, 6, 1, 12, 0, 0)

        alert1 = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.PRICE_THRESHOLD,
            message="Test alert",
            current_price=current_price,
            timestamp=timestamp,
        )
        alert2 = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.PRICE_THRESHOLD,
            message="Test alert",
            current_price=current_price,
            timestamp=timestamp,
        )
        alert3 = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.HIGH_VOLATILITY,
            message="Different alert",
            current_price=current_price,
            timestamp=timestamp,
        )

        assert alert1 == alert2
        assert alert1 != alert3

    def test_price_alert_with_different_prices(self):
        """Should handle price alerts with different prices."""
        symbol = StockSymbol("SHOP")
        low_price = Money(Decimal("50.00"))
        high_price = Money(Decimal("65.00"))

        low_alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.PRICE_THRESHOLD,
            message="Low price alert",
            current_price=low_price,
        )

        high_alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.PRICE_THRESHOLD,
            message="High price alert",
            current_price=high_price,
        )

        assert low_alert.current_price < high_alert.current_price
        assert low_alert.current_price.amount == Decimal("50.00")
        assert high_alert.current_price.amount == Decimal("65.00")

    def test_price_alert_with_trigger_value(self):
        """Should handle price alerts with trigger values."""
        symbol = StockSymbol("CRM")
        current_price = Money(Decimal("200.00"))
        trigger_value = Money(Decimal("190.00"))

        alert = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.PRICE_THRESHOLD,
            message="Price exceeded trigger",
            current_price=current_price,
            trigger_value=trigger_value,
        )

        assert alert.trigger_value == trigger_value
        assert alert.current_price > alert.trigger_value


class TestPriceAnalysis:
    """Test suite for PriceAnalysis value object."""

    def test_create_price_analysis_with_all_fields(self):
        """Should create PriceAnalysis with all required fields."""
        symbol = StockSymbol("AAPL")
        current_price = Money(Decimal("150.00"))
        trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.8"),
            duration_days=30,
            confidence_level=Decimal("0.85"),
        )
        support_levels = [
            Money(Decimal("145.00")),
            Money(Decimal("140.00")),
        ]
        resistance_levels = [
            Money(Decimal("155.00")),
            Money(Decimal("160.00")),
        ]
        momentum_indicators = {
            "rsi": Decimal("65.0"),
            "macd": Decimal("1.5"),
            "stochastic": Decimal("70.0"),
        }
        alerts = [
            PriceAlert(
                symbol=symbol,
                alert_type=AlertType.PRICE_THRESHOLD,
                message="Price near resistance",
                current_price=current_price,
            )
        ]

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            volatility_score=Decimal("0.6"),
            momentum_indicators=momentum_indicators,
            alerts=alerts,
        )

        assert analysis.symbol == symbol
        assert analysis.current_price == current_price
        assert analysis.trend_analysis == trend
        assert analysis.support_levels == support_levels
        assert analysis.resistance_levels == resistance_levels
        assert analysis.volatility_score == Decimal("0.6")
        assert analysis.momentum_indicators == momentum_indicators
        assert analysis.alerts == alerts

    def test_create_price_analysis_with_empty_collections(self):
        """Should create PriceAnalysis with empty support/resistance/alerts."""
        symbol = StockSymbol("MSFT")
        current_price = Money(Decimal("300.00"))
        trend = PriceTrend(
            direction=TrendDirection.SIDEWAYS,
            strength=Decimal("0.3"),
            duration_days=15,
            confidence_level=Decimal("0.7"),
        )

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.4"),
            momentum_indicators={},
            alerts=[],
        )

        assert not analysis.support_levels
        assert not analysis.resistance_levels
        assert not analysis.momentum_indicators
        assert not analysis.alerts

    def test_is_overbought_with_high_rsi(self):
        """Should identify overbought condition when RSI >= 70."""
        symbol = StockSymbol("TSLA")
        current_price = Money(Decimal("200.00"))
        trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.9"),
            duration_days=20,
            confidence_level=Decimal("0.85"),
        )
        momentum_indicators = {"rsi": Decimal("75.0")}

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.8"),
            momentum_indicators=momentum_indicators,
            alerts=[],
        )

        assert analysis.is_overbought is True

    def test_is_overbought_at_boundary(self):
        """Should identify overbought condition at RSI = 70 boundary."""
        symbol = StockSymbol("NVDA")
        current_price = Money(Decimal("400.00"))
        trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.7"),
            duration_days=25,
            confidence_level=Decimal("0.8"),
        )
        momentum_indicators = {"rsi": Decimal("70.0")}

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.7"),
            momentum_indicators=momentum_indicators,
            alerts=[],
        )

        assert analysis.is_overbought is True

    def test_is_overbought_with_low_rsi(self):
        """Should not identify overbought condition when RSI < 70."""
        symbol = StockSymbol("AMD")
        current_price = Money(Decimal("100.00"))
        trend = PriceTrend(
            direction=TrendDirection.SIDEWAYS,
            strength=Decimal("0.5"),
            duration_days=10,
            confidence_level=Decimal("0.6"),
        )
        momentum_indicators = {"rsi": Decimal("65.0")}

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.5"),
            momentum_indicators=momentum_indicators,
            alerts=[],
        )

        assert analysis.is_overbought is False

    def test_is_overbought_without_rsi(self):
        """Should default to not overbought when RSI is not provided."""
        symbol = StockSymbol("INTC")
        current_price = Money(Decimal("50.00"))
        trend = PriceTrend(
            direction=TrendDirection.DOWNWARD,
            strength=Decimal("0.6"),
            duration_days=15,
            confidence_level=Decimal("0.75"),
        )
        momentum_indicators = {"macd": Decimal("-1.0")}  # No RSI

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.6"),
            momentum_indicators=momentum_indicators,
            alerts=[],
        )

        assert analysis.is_overbought is False

    def test_is_oversold_with_low_rsi(self):
        """Should identify oversold condition when RSI <= 30."""
        symbol = StockSymbol("ORCL")
        current_price = Money(Decimal("80.00"))
        trend = PriceTrend(
            direction=TrendDirection.DOWNWARD,
            strength=Decimal("0.8"),
            duration_days=20,
            confidence_level=Decimal("0.9"),
        )
        momentum_indicators = {"rsi": Decimal("25.0")}

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.9"),
            momentum_indicators=momentum_indicators,
            alerts=[],
        )

        assert analysis.is_oversold is True

    def test_is_oversold_at_boundary(self):
        """Should identify oversold condition at RSI = 30 boundary."""
        symbol = StockSymbol("CRM")
        current_price = Money(Decimal("200.00"))
        trend = PriceTrend(
            direction=TrendDirection.DOWNWARD,
            strength=Decimal("0.7"),
            duration_days=18,
            confidence_level=Decimal("0.85"),
        )
        momentum_indicators = {"rsi": Decimal("30.0")}

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.8"),
            momentum_indicators=momentum_indicators,
            alerts=[],
        )

        assert analysis.is_oversold is True

    def test_is_oversold_with_high_rsi(self):
        """Should not identify oversold condition when RSI > 30."""
        symbol = StockSymbol("GOOGL")
        current_price = Money(Decimal("120.00"))
        trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.6"),
            duration_days=12,
            confidence_level=Decimal("0.7"),
        )
        momentum_indicators = {"rsi": Decimal("35.0")}

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.4"),
            momentum_indicators=momentum_indicators,
            alerts=[],
        )

        assert analysis.is_oversold is False

    def test_is_oversold_without_rsi(self):
        """Should default to not oversold when RSI is not provided."""
        symbol = StockSymbol("SHOP")
        current_price = Money(Decimal("50.00"))
        trend = PriceTrend(
            direction=TrendDirection.SIDEWAYS,
            strength=Decimal("0.3"),
            duration_days=8,
            confidence_level=Decimal("0.6"),
        )
        momentum_indicators = {"stochastic": Decimal("20.0")}  # No RSI

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.3"),
            momentum_indicators=momentum_indicators,
            alerts=[],
        )

        assert analysis.is_oversold is False

    def test_rsi_neutral_zone(self):
        """Should be neither overbought nor oversold in neutral RSI range."""
        symbol = StockSymbol("BABA")
        current_price = Money(Decimal("90.00"))
        trend = PriceTrend(
            direction=TrendDirection.SIDEWAYS,
            strength=Decimal("0.4"),
            duration_days=10,
            confidence_level=Decimal("0.65"),
        )
        momentum_indicators = {"rsi": Decimal("50.0")}  # Neutral RSI

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.5"),
            momentum_indicators=momentum_indicators,
            alerts=[],
        )

        assert analysis.is_overbought is False
        assert analysis.is_oversold is False

    def test_price_analysis_is_immutable(self):
        """PriceAnalysis should be immutable (frozen dataclass)."""
        symbol = StockSymbol("V")
        current_price = Money(Decimal("250.00"))
        trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.7"),
            duration_days=20,
            confidence_level=Decimal("0.8"),
        )

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.6"),
            momentum_indicators={"rsi": Decimal("60.0")},
            alerts=[],
        )

        # Attempting to modify should raise AttributeError
        with pytest.raises(AttributeError):
            analysis.symbol = StockSymbol("MA")

        with pytest.raises(AttributeError):
            analysis.current_price = Money(Decimal("260.00"))

        with pytest.raises(AttributeError):
            analysis.volatility_score = Decimal("0.8")

    def test_price_analysis_equality(self):
        """Should compare PriceAnalysis objects for equality."""
        symbol = StockSymbol("JPM")
        current_price = Money(Decimal("140.00"))
        trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.6"),
            duration_days=15,
            confidence_level=Decimal("0.75"),
        )

        analysis1 = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[Money(Decimal("135.00"))],
            resistance_levels=[Money(Decimal("145.00"))],
            volatility_score=Decimal("0.5"),
            momentum_indicators={"rsi": Decimal("55.0")},
            alerts=[],
        )
        analysis2 = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[Money(Decimal("135.00"))],
            resistance_levels=[Money(Decimal("145.00"))],
            volatility_score=Decimal("0.5"),
            momentum_indicators={"rsi": Decimal("55.0")},
            alerts=[],
        )
        analysis3 = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[Money(Decimal("130.00"))],  # Different support
            resistance_levels=[Money(Decimal("145.00"))],
            volatility_score=Decimal("0.5"),
            momentum_indicators={"rsi": Decimal("55.0")},
            alerts=[],
        )

        assert analysis1 == analysis2
        assert analysis1 != analysis3

    def test_price_analysis_with_multiple_momentum_indicators(self):
        """Should handle multiple momentum indicators correctly."""
        symbol = StockSymbol("WMT")
        current_price = Money(Decimal("160.00"))
        trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.65"),
            duration_days=22,
            confidence_level=Decimal("0.8"),
        )
        momentum_indicators = {
            "rsi": Decimal("68.0"),
            "macd": Decimal("2.1"),
            "stochastic": Decimal("75.0"),
            "williams_r": Decimal("-25.0"),
            "cci": Decimal("85.0"),
        }

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.6"),
            momentum_indicators=momentum_indicators,
            alerts=[],
        )

        assert len(analysis.momentum_indicators) == 5
        assert analysis.momentum_indicators["rsi"] == Decimal("68.0")
        assert analysis.momentum_indicators["macd"] == Decimal("2.1")
        assert analysis.momentum_indicators["stochastic"] == Decimal("75.0")
        assert analysis.is_overbought is False  # RSI < 70

    def test_price_analysis_with_multiple_alerts(self):
        """Should handle multiple price alerts correctly."""
        symbol = StockSymbol("DIS")
        current_price = Money(Decimal("100.00"))
        trend = PriceTrend(
            direction=TrendDirection.DOWNWARD,
            strength=Decimal("0.7"),
            duration_days=30,
            confidence_level=Decimal("0.85"),
        )

        alert1 = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.PRICE_THRESHOLD,
            message="Price below support",
            current_price=current_price,
            severity="high",
        )
        alert2 = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.HIGH_VOLATILITY,
            message="Volatility spike detected",
            current_price=current_price,
            severity="medium",
        )
        alert3 = PriceAlert(
            symbol=symbol,
            alert_type=AlertType.TECHNICAL_INDICATOR,
            message="RSI oversold",
            current_price=current_price,
            severity="low",
        )

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[Money(Decimal("95.00"))],
            resistance_levels=[Money(Decimal("105.00"))],
            volatility_score=Decimal("0.9"),
            momentum_indicators={"rsi": Decimal("25.0")},
            alerts=[alert1, alert2, alert3],
        )

        assert len(analysis.alerts) == 3
        assert analysis.alerts[0].severity == "high"
        assert analysis.alerts[1].severity == "medium"
        assert analysis.alerts[2].severity == "low"
        assert analysis.is_oversold is True

    def test_price_analysis_with_multiple_support_resistance_levels(self):
        """Should handle multiple support and resistance levels."""
        symbol = StockSymbol("KO")
        current_price = Money(Decimal("60.00"))
        trend = PriceTrend(
            direction=TrendDirection.UPWARD,
            strength=Decimal("0.6"),
            duration_days=18,
            confidence_level=Decimal("0.75"),
        )

        support_levels = [
            Money(Decimal("58.50")),
            Money(Decimal("57.00")),
            Money(Decimal("55.50")),
        ]
        resistance_levels = [
            Money(Decimal("61.50")),
            Money(Decimal("63.00")),
            Money(Decimal("65.00")),
        ]

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            volatility_score=Decimal("0.4"),
            momentum_indicators={"rsi": Decimal("58.0")},
            alerts=[],
        )

        assert len(analysis.support_levels) == 3
        assert len(analysis.resistance_levels) == 3
        assert analysis.support_levels[0] == Money(Decimal("58.50"))
        assert analysis.resistance_levels[0] == Money(Decimal("61.50"))

    def test_price_analysis_edge_cases(self):
        """Should handle edge cases correctly."""
        symbol = StockSymbol("F")
        current_price = Money(Decimal("12.00"))
        trend = PriceTrend(
            direction=TrendDirection.SIDEWAYS,
            strength=Decimal("0.1"),  # Very weak trend
            duration_days=1,  # Single day
            confidence_level=Decimal("0.5"),  # Low confidence
        )

        # Edge case: RSI exactly between overbought/oversold boundaries
        momentum_indicators = {"rsi": Decimal("50.0")}

        analysis = PriceAnalysis(
            symbol=symbol,
            current_price=current_price,
            trend_analysis=trend,
            support_levels=[],
            resistance_levels=[],
            volatility_score=Decimal("0.0"),  # No volatility
            momentum_indicators=momentum_indicators,
            alerts=[],
        )

        assert analysis.trend_analysis.is_strong_trend is False
        assert analysis.is_overbought is False
        assert analysis.is_oversold is False
        assert analysis.volatility_score == Decimal("0.0")
