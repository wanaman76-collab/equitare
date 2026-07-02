"""
calculations.py — Core weight distribution calculations for EquiTare.

All pure functions: input four pad weights, return derived values.
No side effects, easy to unit-test.

Pad layout (viewed from above):
    FL ---- FR
    |        |
    RL ---- RR
"""

from collections import deque
from typing import Deque

# --- Configuration constants ---

# Minimum load on each pad for the horse to be considered properly standing
MIN_PAD_THRESHOLD_KG: float = 20.0

# Maximum allowed variation (max - min of total_kg) in the rolling window
STABILITY_VARIATION_THRESHOLD_KG: float = 10.0

# Maximum allowed single-reading jump on any individual pad
STABILITY_SPIKE_THRESHOLD_KG: float = 15.0

# Number of recent readings kept for stability analysis
STABILITY_WINDOW_SIZE: int = 5


def calculate_totals(fl: float, fr: float, rl: float, rr: float) -> dict:
    """
    Calculate all derived weight values from four pad readings.

    Args:
        fl, fr, rl, rr: Weight in kg from each hoof pad.

    Returns:
        Dictionary with total_kg, left_kg, right_kg, front_kg, rear_kg,
        left_percent, right_percent, front_percent, rear_percent.
    """
    total = fl + fr + rl + rr

    left = fl + rl
    right = fr + rr
    front = fl + fr
    rear = rl + rr

    # Avoid division-by-zero if all pads are zero (e.g. during tare)
    if total > 0:
        left_pct = (left / total) * 100.0
        right_pct = (right / total) * 100.0
        front_pct = (front / total) * 100.0
        rear_pct = (rear / total) * 100.0
    else:
        left_pct = right_pct = front_pct = rear_pct = 0.0

    return {
        "total_kg": round(total, 2),
        "left_kg": round(left, 2),
        "right_kg": round(right, 2),
        "front_kg": round(front, 2),
        "rear_kg": round(rear, 2),
        "left_percent": round(left_pct, 1),
        "right_percent": round(right_pct, 1),
        "front_percent": round(front_pct, 1),
        "rear_percent": round(rear_pct, 1),
    }


def check_stability(
    fl: float,
    fr: float,
    rl: float,
    rr: float,
    history: Deque[float],
    prev_fl: float | None = None,
    prev_fr: float | None = None,
    prev_rl: float | None = None,
    prev_rr: float | None = None,
) -> tuple[bool, str]:
    """
    Determine whether the current reading represents a stable stance.

    Stability criteria:
    1. All four pads are above MIN_PAD_THRESHOLD_KG (horse is fully standing).
    2. The rolling window of total weights has low variation.
    3. No individual pad has spiked by more than STABILITY_SPIKE_THRESHOLD_KG
       compared to the previous reading (only checked when previous values are provided).

    Args:
        fl, fr, rl, rr: Current pad readings in kg.
        history: A deque of recent total_kg values (updated externally).
        prev_fl, prev_fr, prev_rl, prev_rr: Previous pad readings for spike detection.
            Pass None (default) to skip spike detection — used for the first reading.

    Returns:
        Tuple of (is_stable: bool, reason: str)
    """
    total = fl + fr + rl + rr

    # Check 1: all pads loaded
    for name, value in [("FL", fl), ("FR", fr), ("RL", rl), ("RR", rr)]:
        if value < MIN_PAD_THRESHOLD_KG:
            return False, f"Pad {name} below minimum threshold ({value:.1f} kg < {MIN_PAD_THRESHOLD_KG} kg)"

    # Check 2: rolling window variation
    if len(history) >= 2:
        variation = max(history) - min(history)
        if variation > STABILITY_VARIATION_THRESHOLD_KG:
            return False, f"Total weight unstable (variation {variation:.1f} kg over last {len(history)} readings)"

    # Check 3: no sudden spike on any individual pad (skip if no previous reading)
    if prev_fl is not None:
        for name, curr, prev in [
            ("FL", fl, prev_fl),
            ("FR", fr, prev_fr),
            ("RL", rl, prev_rl),
            ("RR", rr, prev_rr),
        ]:
            spike = abs(curr - (prev or 0.0))
            if spike > STABILITY_SPIKE_THRESHOLD_KG:
                return False, f"Spike detected on pad {name} ({spike:.1f} kg jump)"

    return True, f"Stable ({total:.1f} kg, {len(history)}-reading window OK)"
