"""
simulator.py — Generate realistic simulated horse hoof readings for development.

This module lets you test the whole system without real hardware.
A typical horse weighs roughly 350–600 kg.  The simulator distributes
weight across four pads with small random drift to mimic natural weight shifting.

Two modes:
  - "stable": readings that will pass the stability checker.
  - "unstable": readings with large spikes / low pad loads to trigger instability.
"""

import random
from collections import deque
from typing import Deque, Optional

from app.calculations import calculate_totals, check_stability, STABILITY_WINDOW_SIZE

# Realistic horse weight range
HORSE_WEIGHT_MIN_KG = 350.0
HORSE_WEIGHT_MAX_KG = 600.0

# In stable mode, how much the total can drift per reading (kept small so the
# rolling-window variation check passes).
STABLE_DRIFT_KG = 2.0

# Internal history buffer for stability calculation
_history: Deque[float] = deque(maxlen=STABILITY_WINDOW_SIZE)
_prev: dict[str, Optional[float]] = {"FL": None, "FR": None, "RL": None, "RR": None}

# Running per-pad values used to generate gradual drift (stable mode only)
_current_pads: dict[str, float] = {"FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0}
_initialized: bool = False


def _init_pads() -> None:
    """Pick a random starting weight and distribute it across the four pads."""
    global _current_pads, _initialized
    total = random.uniform(HORSE_WEIGHT_MIN_KG, HORSE_WEIGHT_MAX_KG)
    fl, fr, rl, rr = _distribute(total)
    _current_pads = {"FL": fl, "FR": fr, "RL": rl, "RR": rr}
    _initialized = True


def _distribute(total: float) -> tuple[float, float, float, float]:
    """
    Split total weight across four pads with slight randomness.

    Typical horse distribution: ~55–60 % on front, slight left/right variation.
    """
    front_share = random.uniform(0.50, 0.62)
    left_share = random.uniform(0.46, 0.54)

    front = total * front_share
    rear = total * (1 - front_share)

    fl = front * left_share
    fr = front * (1 - left_share)
    rl = rear * left_share
    rr = rear * (1 - left_share)

    return round(fl, 2), round(fr, 2), round(rl, 2), round(rr, 2)


def generate_reading(mode: str = "stable") -> dict:
    """
    Generate a single simulated hoof reading.

    Args:
        mode: "stable" for gentle drift, "unstable" for spiky / low-pad data.

    Returns:
        A dict matching the HoofReading model fields (without timestamp,
        which is added by the endpoint).
    """
    global _current_pads, _initialized

    if mode == "unstable":
        return _generate_unstable()

    # --- Stable mode ---
    # On first call, initialise a base weight
    if not _initialized:
        _init_pads()

    # Apply tiny per-pad drift so readings look natural
    for pad in ("FL", "FR", "RL", "RR"):
        drift = random.uniform(-STABLE_DRIFT_KG, STABLE_DRIFT_KG)
        _current_pads[pad] = max(_current_pads[pad] + drift, 30.0)

    fl = _current_pads["FL"]
    fr = _current_pads["FR"]
    rl = _current_pads["RL"]
    rr = _current_pads["RR"]

    return _build_reading(fl, fr, rl, rr)


def _generate_unstable() -> dict:
    """
    Generate a reading that is intentionally unstable.
    Randomly produces either a low-pad situation or a large spike.
    """
    total = random.uniform(HORSE_WEIGHT_MIN_KG, HORSE_WEIGHT_MAX_KG)
    fl, fr, rl, rr = _distribute(total)

    unstable_type = random.choice(["low_pad", "spike"])

    if unstable_type == "low_pad":
        # One pad is nearly unloaded (horse lifting a hoof)
        pad = random.choice(["fl", "fr", "rl", "rr"])
        pads = {"fl": fl, "fr": fr, "rl": rl, "rr": rr}
        pads[pad] = random.uniform(0.0, 15.0)
        fl, fr, rl, rr = pads["fl"], pads["fr"], pads["rl"], pads["rr"]
    else:
        # One pad spikes upward suddenly
        spike = random.uniform(30.0, 60.0)
        pad = random.choice(["fl", "fr", "rl", "rr"])
        if pad == "fl":
            fl += spike
        elif pad == "fr":
            fr += spike
        elif pad == "rl":
            rl += spike
        else:
            rr += spike

    return _build_reading(fl, fr, rl, rr)


def _build_reading(fl: float, fr: float, rl: float, rr: float) -> dict:
    """Combine pad values into a full reading dict including stability check."""
    global _prev, _history

    totals = calculate_totals(fl, fr, rl, rr)

    # Capture whether a previous reading exists BEFORE appending the current total.
    # This determines whether spike detection should be applied.
    has_previous_reading = len(_history) > 0

    _history.append(totals["total_kg"])

    is_stable, stability_reason = check_stability(
        fl, fr, rl, rr,
        history=_history,
        prev_fl=_prev["FL"] if has_previous_reading else None,
        prev_fr=_prev["FR"] if has_previous_reading else None,
        prev_rl=_prev["RL"] if has_previous_reading else None,
        prev_rr=_prev["RR"] if has_previous_reading else None,
    )

    _prev = {"FL": fl, "FR": fr, "RL": rl, "RR": rr}

    return {
        "fl_kg": round(fl, 2),
        "fr_kg": round(fr, 2),
        "rl_kg": round(rl, 2),
        "rr_kg": round(rr, 2),
        **totals,
        "is_stable": is_stable,
        "stability_reason": stability_reason,
    }


def reset() -> None:
    """Reset the simulator history (useful for test isolation)."""
    global _prev, _history, _initialized, _current_pads
    _history.clear()
    _prev = {"FL": None, "FR": None, "RL": None, "RR": None}
    _current_pads = {"FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0}
    _initialized = False

