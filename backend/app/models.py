"""
models.py — Pydantic data models for EquiTare readings and responses.

These models define the shape of the data flowing through the API.
Pydantic handles validation automatically, which is good for an R&D prototype.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class HoofReading(BaseModel):
    """
    A single measurement snapshot from all four hoof pads.

    Fields:
        fl_kg, fr_kg, rl_kg, rr_kg  — individual pad weights in kilograms
        total_kg                     — sum of all four pads
        left_kg / right_kg           — left (FL+RL) and right (FR+RR) loads
        front_kg / rear_kg           — front (FL+FR) and rear (RL+RR) loads
        left_percent / right_percent — side distribution as percentages
        front_percent / rear_percent — fore-aft distribution as percentages
        is_stable                    — True if the stance passes stability checks
        stability_reason             — human-readable explanation of stability result
    """
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Individual pad weights
    fl_kg: float = Field(..., description="Front-Left pad weight in kg")
    fr_kg: float = Field(..., description="Front-Right pad weight in kg")
    rl_kg: float = Field(..., description="Rear-Left pad weight in kg")
    rr_kg: float = Field(..., description="Rear-Right pad weight in kg")

    # Derived totals
    total_kg: float = Field(..., description="Total estimated horse weight in kg")
    left_kg: float = Field(..., description="Combined left-side weight (FL + RL)")
    right_kg: float = Field(..., description="Combined right-side weight (FR + RR)")
    front_kg: float = Field(..., description="Combined front weight (FL + FR)")
    rear_kg: float = Field(..., description="Combined rear weight (RL + RR)")

    # Distribution percentages
    left_percent: float = Field(..., description="Left-side share of total weight (%)")
    right_percent: float = Field(..., description="Right-side share of total weight (%)")
    front_percent: float = Field(..., description="Front share of total weight (%)")
    rear_percent: float = Field(..., description="Rear share of total weight (%)")

    # Stability
    is_stable: bool = Field(..., description="True if the reading is considered stable")
    stability_reason: str = Field(..., description="Short explanation of stability result")


class SimulateRequest(BaseModel):
    """Request body for POST /api/readings/simulate."""
    mode: str = Field(
        default="stable",
        description="Simulation mode: 'stable' or 'unstable'"
    )


class TareRequest(BaseModel):
    """Request body for POST /api/calibration/tare — no fields needed, tares all pads."""
    pass


class SetKnownLoadRequest(BaseModel):
    """
    Request body for POST /api/calibration/set-known-load.

    Provide the pad name and the known physical load in kg.
    The backend will use the current raw sensor value to compute a new scale factor.
    """
    pad: str = Field(..., description="Pad name: FL, FR, RL, or RR")
    known_kg: float = Field(..., description="Physically known weight placed on this pad (kg)")


class CalibrationState(BaseModel):
    """Current calibration values returned by GET /api/calibration."""
    tare_offsets: dict = Field(..., description="Raw offset applied to each pad before scaling")
    scale_factors: dict = Field(..., description="Divisor used to convert raw units to kg")


class SessionInfo(BaseModel):
    """Metadata about a measurement session."""
    session_id: str
    started_at: datetime
    stopped_at: Optional[datetime] = None
    readings: list[HoofReading] = Field(default_factory=list)
    is_active: bool = True


class HealthResponse(BaseModel):
    """Response for GET /health."""
    status: str = "ok"
    version: str = "0.1.0"
