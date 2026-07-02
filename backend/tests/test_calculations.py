"""
test_calculations.py — Unit tests for the EquiTare calculations module.

Tests verify:
  - Total weight calculation
  - Left / right weight split
  - Front / rear weight split
  - Percentage distribution
  - Stable stance detection (various scenarios)
"""

import pytest
from collections import deque

# Import the functions under test
from app.calculations import (
    calculate_totals,
    check_stability,
    MIN_PAD_THRESHOLD_KG,
    STABILITY_VARIATION_THRESHOLD_KG,
    STABILITY_SPIKE_THRESHOLD_KG,
    STABILITY_WINDOW_SIZE,
)


# ---------------------------------------------------------------------------
# calculate_totals
# ---------------------------------------------------------------------------

def test_total_weight():
    """Total should be the sum of all four pads."""
    result = calculate_totals(fl=100, fr=110, rl=90, rr=95)
    assert result["total_kg"] == pytest.approx(395.0)


def test_left_right_split():
    """Left = FL + RL, Right = FR + RR."""
    result = calculate_totals(fl=100, fr=120, rl=80, rr=100)
    assert result["left_kg"] == pytest.approx(180.0)   # 100 + 80
    assert result["right_kg"] == pytest.approx(220.0)  # 120 + 100


def test_front_rear_split():
    """Front = FL + FR, Rear = RL + RR."""
    result = calculate_totals(fl=100, fr=120, rl=80, rr=100)
    assert result["front_kg"] == pytest.approx(220.0)  # 100 + 120
    assert result["rear_kg"] == pytest.approx(180.0)   # 80 + 100


def test_percentages_sum_to_100():
    """Left + Right percentages should sum to 100%, same for Front + Rear."""
    result = calculate_totals(fl=110, fr=90, rl=105, rr=95)
    assert result["left_percent"] + result["right_percent"] == pytest.approx(100.0, abs=0.1)
    assert result["front_percent"] + result["rear_percent"] == pytest.approx(100.0, abs=0.1)


def test_equal_weight_gives_50_percent():
    """Identical pad values should give 50/50 split."""
    result = calculate_totals(fl=100, fr=100, rl=100, rr=100)
    assert result["left_percent"] == pytest.approx(50.0)
    assert result["right_percent"] == pytest.approx(50.0)
    assert result["front_percent"] == pytest.approx(50.0)
    assert result["rear_percent"] == pytest.approx(50.0)


def test_all_zero_pads_returns_zero_percentages():
    """No division-by-zero when all pads are zero."""
    result = calculate_totals(fl=0, fr=0, rl=0, rr=0)
    assert result["total_kg"] == 0.0
    assert result["left_percent"] == 0.0
    assert result["right_percent"] == 0.0


# ---------------------------------------------------------------------------
# check_stability
# ---------------------------------------------------------------------------

def _stable_history():
    """Helper: create a deque with consistent total values (stable window)."""
    h = deque(maxlen=STABILITY_WINDOW_SIZE)
    for _ in range(STABILITY_WINDOW_SIZE):
        h.append(400.0)
    return h


def test_stable_reading_passes():
    """A perfectly steady reading with a stable history should pass."""
    h = _stable_history()
    is_stable, reason = check_stability(
        fl=100, fr=100, rl=100, rr=100,
        history=h,
        prev_fl=100, prev_fr=100, prev_rl=100, prev_rr=100,
    )
    assert is_stable is True
    assert "Stable" in reason


def test_low_pad_fails_stability():
    """A pad below the minimum threshold should mark the reading as unstable."""
    h = _stable_history()
    is_stable, reason = check_stability(
        fl=5.0, fr=100, rl=100, rr=100,  # FL is far too low
        history=h,
    )
    assert is_stable is False
    assert "FL" in reason


def test_high_variation_window_fails():
    """Large variation in the rolling window should cause instability."""
    h = deque(maxlen=STABILITY_WINDOW_SIZE)
    h.append(400.0)
    h.append(450.0)  # 50 kg variation — above the threshold
    is_stable, reason = check_stability(
        fl=110, fr=110, rl=115, rr=115,
        history=h,
    )
    assert is_stable is False
    assert "unstable" in reason.lower()


def test_spike_on_pad_fails_stability():
    """A sudden large jump on a single pad should trigger instability."""
    h = _stable_history()
    is_stable, reason = check_stability(
        fl=130, fr=100, rl=100, rr=100,
        history=h,
        prev_fl=100,  # 30 kg jump on FL > threshold
        prev_fr=100,
        prev_rl=100,
        prev_rr=100,
    )
    assert is_stable is False
    assert "FL" in reason


def test_stability_with_empty_history():
    """An empty history window should not crash and should pass variation check."""
    h = deque(maxlen=STABILITY_WINDOW_SIZE)
    is_stable, reason = check_stability(
        fl=100, fr=100, rl=100, rr=100,
        history=h,
    )
    # With an empty history there's no variation to fail on — pads are all loaded
    assert is_stable is True
