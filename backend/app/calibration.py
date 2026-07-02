"""
calibration.py — Per-pad tare offset and scale factor management.

How calibration works in EquiTare:
    1. Tare: With no weight on a pad, record the raw sensor output as the
       zero offset. Subtract this offset from all future readings.
    2. Scale factor: Place a known weight on a pad, divide the
       (raw - tare_offset) by the known weight to get counts-per-kg.
       Apply this divisor to convert any future raw reading to kg.

    kg = (raw - tare_offset) / scale_factor

Persistence note:
    Calibration is kept in memory for now.  To add JSON file persistence
    later, replace _save() / _load() stubs with file I/O — the rest of
    the module stays unchanged.
"""

import logging

logger = logging.getLogger(__name__)

# Default calibration values used before any real calibration is done.
# A scale_factor of 1.0 means the raw value is returned as-is (placeholder).
_DEFAULT_TARE: float = 0.0
_DEFAULT_SCALE: float = 1.0

# Pad names accepted by the calibration module
PAD_NAMES = ("FL", "FR", "RL", "RR")


class CalibrationStore:
    """
    Holds tare offsets and scale factors for all four hoof pads.

    Example usage:
        store = CalibrationStore()
        store.tare(raw_readings={"FL": 50000, "FR": 48000, "RL": 49000, "RR": 51000})
        kg_fl = store.to_kg("FL", raw_value=150000)
    """

    def __init__(self):
        self._tare_offsets: dict[str, float] = {pad: _DEFAULT_TARE for pad in PAD_NAMES}
        self._scale_factors: dict[str, float] = {pad: _DEFAULT_SCALE for pad in PAD_NAMES}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def tare(self, raw_readings: dict[str, float]) -> None:
        """
        Record the current raw readings as the zero point for each pad.

        Args:
            raw_readings: Dict mapping pad name -> current raw sensor value.
                          Only pads present in the dict are updated.
        """
        for pad, raw in raw_readings.items():
            if pad not in PAD_NAMES:
                logger.warning("Unknown pad '%s' in tare call — skipped.", pad)
                continue
            self._tare_offsets[pad] = float(raw)
            logger.info("Tare set for %s: offset = %.2f", pad, raw)

    def set_scale_factor(self, pad: str, raw_value: float, known_kg: float) -> float:
        """
        Calculate and store a new scale factor for a pad given a known weight.

        scale_factor = (raw_value - tare_offset) / known_kg

        Args:
            pad:       Pad name (FL, FR, RL, RR).
            raw_value: Raw sensor reading with the known weight applied.
            known_kg:  The physically measured weight placed on the pad.

        Returns:
            The computed scale factor.

        Raises:
            ValueError: if known_kg is zero or pad name is invalid.
        """
        if pad not in PAD_NAMES:
            raise ValueError(f"Unknown pad name: '{pad}'. Must be one of {PAD_NAMES}.")
        if known_kg <= 0:
            raise ValueError("known_kg must be a positive number.")

        net_raw = raw_value - self._tare_offsets[pad]
        factor = net_raw / known_kg
        self._scale_factors[pad] = factor
        logger.info(
            "Scale factor updated for %s: factor = %.4f (raw=%d, known=%.2f kg)",
            pad, factor, raw_value, known_kg
        )
        return factor

    def to_kg(self, pad: str, raw_value: float) -> float:
        """
        Convert a raw sensor value to kilograms using stored calibration.

        kg = (raw - tare_offset) / scale_factor

        Returns 0.0 if the scale factor is zero to avoid division errors.
        """
        if pad not in PAD_NAMES:
            raise ValueError(f"Unknown pad name: '{pad}'.")

        offset = self._tare_offsets[pad]
        factor = self._scale_factors[pad]

        if factor == 0.0:
            logger.warning("Scale factor for %s is 0 — returning 0 kg.", pad)
            return 0.0

        return (raw_value - offset) / factor

    def get_state(self) -> dict:
        """Return a snapshot of current calibration values (for API/logging)."""
        return {
            "tare_offsets": dict(self._tare_offsets),
            "scale_factors": dict(self._scale_factors),
        }

    # ------------------------------------------------------------------
    # Persistence stubs — replace with JSON file I/O when ready
    # ------------------------------------------------------------------

    def _save(self) -> None:
        """
        Stub: persist calibration to disk.
        Replace with: json.dump(self.get_state(), open("calibration.json","w"))
        """
        pass

    def _load(self) -> None:
        """
        Stub: load calibration from disk.
        Replace with reading calibration.json and populating _tare_offsets / _scale_factors.
        """
        pass


# Module-level singleton — one shared calibration state for the application lifetime.
calibration_store = CalibrationStore()
