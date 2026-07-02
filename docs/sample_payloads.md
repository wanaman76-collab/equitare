# EquiTare — Sample API Payloads

This document shows example request/response payloads for every API endpoint.
Use these as a quick reference when testing with curl, Postman, or the frontend.

---

## GET /health

**Response**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

## GET /api/readings/latest

Returns the most recently generated reading, or `null` if none exists.

**Response (reading present)**
```json
{
  "timestamp": "2024-06-01T10:23:45.123456",
  "fl_kg": 112.3,
  "fr_kg": 108.7,
  "rl_kg": 95.1,
  "rr_kg": 98.4,
  "total_kg": 414.5,
  "left_kg": 207.4,
  "right_kg": 207.1,
  "front_kg": 221.0,
  "rear_kg": 193.5,
  "left_percent": 50.0,
  "right_percent": 50.0,
  "front_percent": 53.3,
  "rear_percent": 46.7,
  "is_stable": true,
  "stability_reason": "Stable (414.5 kg, 5-reading window OK)"
}
```

**Response (no reading yet)**
```json
null
```

---

## POST /api/readings/simulate

**Request**
```json
{
  "mode": "stable"
}
```

Allowed values for `mode`: `"stable"` | `"unstable"`

**Response** — same shape as `/api/readings/latest`

**Unstable example** (one pad too low):
```json
{
  "timestamp": "2024-06-01T10:23:50.000000",
  "fl_kg": 8.2,
  "fr_kg": 110.1,
  "rl_kg": 98.4,
  "rr_kg": 102.3,
  "total_kg": 319.0,
  "left_kg": 106.6,
  "right_kg": 212.4,
  "front_kg": 118.3,
  "rear_kg": 200.7,
  "left_percent": 33.4,
  "right_percent": 66.6,
  "front_percent": 37.1,
  "rear_percent": 62.9,
  "is_stable": false,
  "stability_reason": "Pad FL below minimum threshold (8.2 kg < 20.0 kg)"
}
```

---

## POST /api/calibration/tare

No request body required (send `{}`).

**Response**
```json
{
  "message": "Tare applied to all pads.",
  "offsets": {
    "FL": 112.3,
    "FR": 108.7,
    "RL": 95.1,
    "RR": 98.4
  }
}
```

---

## POST /api/calibration/set-known-load

**Request**
```json
{
  "pad": "FL",
  "known_kg": 20.0
}
```

**Response**
```json
{
  "message": "Scale factor updated for FL.",
  "scale_factor": 5.615
}
```

---

## GET /api/calibration

**Response**
```json
{
  "tare_offsets": {
    "FL": 112.3,
    "FR": 108.7,
    "RL": 95.1,
    "RR": 98.4
  },
  "scale_factors": {
    "FL": 5.615,
    "FR": 1.0,
    "RL": 1.0,
    "RR": 1.0
  }
}
```

---

## POST /api/session/start

No request body required.

**Response**
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "started_at": "2024-06-01T10:25:00.000000",
  "stopped_at": null,
  "readings": [],
  "is_active": true
}
```

**Error (session already active) — HTTP 409**
```json
{
  "detail": "A session is already active. Stop it before starting a new one."
}
```

---

## POST /api/session/stop

No request body required.

**Response** — same shape as `/api/session/start`, but with `stopped_at` populated,
`is_active: false`, and `readings` containing all readings captured during the session.

**Error (no active session) — HTTP 409**
```json
{
  "detail": "No active session to stop."
}
```

---

## GET /api/session/current

Returns the active session or `null`.

---

## GET /api/session/history

Returns an array of all completed sessions (oldest first).

```json
[
  {
    "session_id": "a1b2c3d4-...",
    "started_at": "2024-06-01T10:25:00",
    "stopped_at": "2024-06-01T10:30:00",
    "readings": [ ... ],
    "is_active": false
  }
]
```

---

## ESP32 Serial JSON (firmware)

Each line output by the firmware over USB Serial:

```json
{
  "timestamp_ms": 123456,
  "fl_raw": 100200,
  "fr_raw": 102400,
  "rl_raw": 98100,
  "rr_raw": 99300,
  "fl_kg": 110.5,
  "fr_kg": 112.0,
  "rl_kg": 105.2,
  "rr_kg": 108.8
}
```

This format maps directly to the `fl_kg`, `fr_kg`, `rl_kg`, `rr_kg` fields in the backend
`HoofReading` model.  A future `serial_reader.py` module will read this stream,
call `calculate_totals()` and `check_stability()`, and push the result to the backend.
