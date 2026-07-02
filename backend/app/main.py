"""
main.py — FastAPI application for EquiTare backend.

Endpoints:
  GET  /health                         System health check
  GET  /api/readings/latest            Get the most recent simulated reading
  POST /api/readings/simulate          Generate a new simulated reading
  POST /api/calibration/tare           Zero all pad offsets
  POST /api/calibration/set-known-load Set scale factor from a known weight
  GET  /api/calibration                Inspect current calibration values
  POST /api/session/start              Start a measurement session
  POST /api/session/stop               Stop the current session
  GET  /api/session/current            Get the current active session
  GET  /api/session/history            List all completed sessions

Run with:
    uvicorn app.main:app --reload --port 8000
"""

from datetime import datetime
from collections import deque

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    HoofReading,
    SimulateRequest,
    SetKnownLoadRequest,
    CalibrationState,
    SessionInfo,
    HealthResponse,
    TareRequest,
)
from app.calculations import STABILITY_WINDOW_SIZE, calculate_totals, check_stability
from app.calibration import calibration_store
from app.simulator import generate_reading, reset as reset_simulator
from app.session_store import session_store

app = FastAPI(
    title="EquiTare API",
    description="Low-cost distributed hoof weight measurement system for horses.",
    version="0.1.0",
)

# Allow all origins during development so the frontend dev server can connect.
# Restrict this in production to the actual frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rolling window of recent total weights for stability tracking
_reading_history: deque = deque(maxlen=STABILITY_WINDOW_SIZE)
_latest_reading: HoofReading | None = None

# Previous pad values for spike detection
_prev_pads: dict[str, float] = {"FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    """Simple health check — confirms the API is running."""
    return HealthResponse()


# ---------------------------------------------------------------------------
# Readings
# ---------------------------------------------------------------------------

@app.get("/api/readings/latest", response_model=HoofReading | None, tags=["Readings"])
def get_latest_reading():
    """
    Return the most recently generated reading.

    Returns null (HTTP 200 with null body) if no reading has been generated yet.
    The frontend polls this to update the live display.
    """
    return _latest_reading


@app.post("/api/readings/simulate", response_model=HoofReading, tags=["Readings"])
def simulate_reading(request: SimulateRequest):
    """
    Generate a new simulated reading and store it as the latest.

    The reading is also appended to the active session (if one exists).
    """
    global _latest_reading, _prev_pads

    if request.mode not in ("stable", "unstable"):
        raise HTTPException(status_code=400, detail="mode must be 'stable' or 'unstable'")

    raw = generate_reading(mode=request.mode)

    reading = HoofReading(
        timestamp=datetime.utcnow(),
        **raw,
    )

    _latest_reading = reading
    _reading_history.append(reading.total_kg)
    _prev_pads = {
        "FL": reading.fl_kg,
        "FR": reading.fr_kg,
        "RL": reading.rl_kg,
        "RR": reading.rr_kg,
    }

    session_store.add_reading(reading)
    return reading


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------

@app.post("/api/calibration/tare", tags=["Calibration"])
def tare():
    """
    Zero all pad offsets using the current raw reading values.

    In a real system this uses live sensor data.  For the simulator we use
    a simulated reading as a placeholder — in practice you would call this
    with no load on the pads.
    """
    # Use the latest reading's "raw" values as the tare baseline.
    # In a hardware system, raw values come directly from the HX711 driver.
    if _latest_reading is None:
        # No reading yet — reset calibration to zero offsets
        calibration_store.tare({"FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0})
    else:
        calibration_store.tare({
            "FL": _latest_reading.fl_kg,
            "FR": _latest_reading.fr_kg,
            "RL": _latest_reading.rl_kg,
            "RR": _latest_reading.rr_kg,
        })

    return {"message": "Tare applied to all pads.", "offsets": calibration_store.get_state()["tare_offsets"]}


@app.post("/api/calibration/set-known-load", tags=["Calibration"])
def set_known_load(request: SetKnownLoadRequest):
    """
    Update the scale factor for a specific pad given a known physical load.

    Place a weight of known_kg on the pad, then call this endpoint.
    The backend reads the current sensor value and calculates the correct factor.
    """
    pad = request.pad.upper()
    pad_map = {
        "FL": _latest_reading.fl_kg if _latest_reading else 0.0,
        "FR": _latest_reading.fr_kg if _latest_reading else 0.0,
        "RL": _latest_reading.rl_kg if _latest_reading else 0.0,
        "RR": _latest_reading.rr_kg if _latest_reading else 0.0,
    }

    if pad not in pad_map:
        raise HTTPException(status_code=400, detail=f"Unknown pad '{pad}'.")

    try:
        factor = calibration_store.set_scale_factor(
            pad=pad,
            raw_value=pad_map[pad],
            known_kg=request.known_kg,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"message": f"Scale factor updated for {pad}.", "scale_factor": factor}


@app.get("/api/calibration", response_model=CalibrationState, tags=["Calibration"])
def get_calibration():
    """Return current tare offsets and scale factors for all pads."""
    state = calibration_store.get_state()
    return CalibrationState(**state)


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

@app.post("/api/session/start", response_model=SessionInfo, tags=["Sessions"])
def start_session():
    """Start a new measurement session."""
    try:
        return session_store.start_session()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@app.post("/api/session/stop", response_model=SessionInfo, tags=["Sessions"])
def stop_session():
    """Stop the currently active session and archive it."""
    try:
        return session_store.stop_session()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@app.get("/api/session/current", response_model=SessionInfo | None, tags=["Sessions"])
def current_session():
    """Return the currently active session, or null if none is active."""
    return session_store.current_session()


@app.get("/api/session/history", response_model=list[SessionInfo], tags=["Sessions"])
def session_history():
    """Return all completed sessions (oldest first)."""
    return session_store.session_history()
