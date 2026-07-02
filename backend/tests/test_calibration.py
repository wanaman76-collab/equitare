"""
test_calibration.py — Unit tests for the CalibrationStore.

Tests verify:
  - Default state (no calibration applied)
  - Tare: sets offset, zeroes output at tare point
  - Scale factor: raw-to-kg conversion
  - Known load calculation
  - Error handling for invalid inputs
"""

import pytest
from app.calibration import CalibrationStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def store():
    """Fresh CalibrationStore for each test."""
    return CalibrationStore()


# ---------------------------------------------------------------------------
# Default state
# ---------------------------------------------------------------------------

def test_default_to_kg_returns_raw_value(store):
    """
    With default scale factor 1.0 and tare offset 0.0,
    to_kg should return the raw value unchanged.
    """
    assert store.to_kg("FL", 12345.0) == pytest.approx(12345.0)


def test_default_state_has_all_pads(store):
    """get_state should contain entries for all four pads."""
    state = store.get_state()
    for pad in ("FL", "FR", "RL", "RR"):
        assert pad in state["tare_offsets"]
        assert pad in state["scale_factors"]


# ---------------------------------------------------------------------------
# Tare
# ---------------------------------------------------------------------------

def test_tare_sets_offset(store):
    """After tare, to_kg with the tare raw value should return 0."""
    tare_raw = 50000.0
    store.tare({"FL": tare_raw})
    assert store.to_kg("FL", tare_raw) == pytest.approx(0.0)


def test_tare_multiple_pads(store):
    """Tare all four pads at once."""
    store.tare({"FL": 1000, "FR": 2000, "RL": 1500, "RR": 1800})
    assert store.to_kg("FL", 1000) == pytest.approx(0.0)
    assert store.to_kg("FR", 2000) == pytest.approx(0.0)
    assert store.to_kg("RL", 1500) == pytest.approx(0.0)
    assert store.to_kg("RR", 1800) == pytest.approx(0.0)


def test_tare_unknown_pad_is_ignored(store):
    """Taring an unknown pad name should not raise; others are unaffected."""
    store.tare({"XX": 9999})  # Should not crash
    # FL should still have default offset of 0
    assert store.to_kg("FL", 100.0) == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# Scale factor / raw → kg conversion
# ---------------------------------------------------------------------------

def test_set_scale_factor_and_convert(store):
    """
    With a known load of 100 kg and raw reading of 100,000 counts
    (after tare), scale_factor = 1000.
    to_kg(100_000) should return 100.0 kg.
    """
    store.tare({"FL": 0.0})  # zero offset for simplicity
    store.set_scale_factor(pad="FL", raw_value=100_000.0, known_kg=100.0)
    assert store.to_kg("FL", 100_000.0) == pytest.approx(100.0)


def test_scale_factor_proportional(store):
    """Double the raw value should give double the kg."""
    store.tare({"FR": 0.0})
    store.set_scale_factor("FR", raw_value=50_000.0, known_kg=50.0)
    # scale_factor = 1000
    assert store.to_kg("FR", 100_000.0) == pytest.approx(100.0)


def test_tare_offset_applied_before_scale(store):
    """
    Tare at 10_000 raw, then set factor with raw=110_000 → known=100 kg.
    scale_factor = (110_000 - 10_000) / 100 = 1000.
    to_kg(60_000) = (60_000 - 10_000) / 1000 = 50.0 kg.
    """
    store.tare({"RL": 10_000.0})
    store.set_scale_factor("RL", raw_value=110_000.0, known_kg=100.0)
    assert store.to_kg("RL", 60_000.0) == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_set_scale_factor_zero_known_kg_raises(store):
    """Providing known_kg=0 should raise a ValueError."""
    with pytest.raises(ValueError, match="positive"):
        store.set_scale_factor("FL", raw_value=50_000.0, known_kg=0.0)


def test_set_scale_factor_invalid_pad_raises(store):
    """Providing an invalid pad name should raise a ValueError."""
    with pytest.raises(ValueError, match="Unknown pad"):
        store.set_scale_factor("XX", raw_value=50_000.0, known_kg=100.0)


def test_to_kg_invalid_pad_raises(store):
    """to_kg with an unknown pad name should raise a ValueError."""
    with pytest.raises(ValueError, match="Unknown pad"):
        store.to_kg("ZZ", 100.0)
