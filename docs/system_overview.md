# EquiTare System Overview

## What is EquiTare?

EquiTare is an engineering R&D prototype for **distributed hoof weight measurement** in horses.
Instead of a single large platform scale, it uses four small, low-profile hoof pads — one under each hoof — to capture individual and total weight, plus left/right and front/rear balance.

> ⚠️ This is a student/internship prototype. It is **not** a certified veterinary instrument or commercial weighing scale.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (React)                         │
│  Dashboard: live readings, balance summary, session, calibration│
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST (JSON)
┌──────────────────────────▼──────────────────────────────────────┐
│                    FastAPI Backend (Python)                      │
│  main.py · models.py · calculations.py                          │
│  calibration.py · simulator.py · session_store.py               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ future: pyserial JSON reader
┌──────────────────────────▼──────────────────────────────────────┐
│              ESP32 Firmware (Arduino C++)                        │
│  4× HX711 ADC → raw counts → JSON over USB Serial              │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HX711 differential signal
┌──────────────────────────▼──────────────────────────────────────┐
│   Hoof Pads: FL · FR · RL · RR  (load cell + strain gauge)      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pad Layout

```
Horse viewed from above:

    FL ────── FR
    │          │
   (front)     │
    │          │
    RL ────── RR
```

---

## Core Calculations

| Measurement | Formula |
|-------------|---------|
| Total weight | FL + FR + RL + RR |
| Left load | FL + RL |
| Right load | FR + RR |
| Front load | FL + FR |
| Rear load | RL + RR |
| Left % | Left / Total × 100 |
| Right % | Right / Total × 100 |
| Front % | Front / Total × 100 |
| Rear % | Rear / Total × 100 |

Typical horse front/rear distribution: ~55–60 % on front legs.

---

## Stability Detection

Before saving a measurement the system checks whether the horse is in a stable, four-square stance:

1. **All pads loaded** — each pad must read above a minimum threshold (default: 20 kg).  A pad near zero suggests the horse is lifting a hoof.
2. **Low total variation** — the rolling window of recent total weights must have a range below a configurable threshold (default: 10 kg).
3. **No sudden spikes** — no individual pad should jump by more than 15 kg between consecutive readings.

If all three checks pass, `is_stable = true` and the reading is considered usable for reporting.

---

## Calibration

### Tare
With no load on a pad, the raw sensor output (in ADC counts) becomes the **zero offset** for that pad.  All subsequent readings subtract this offset.

### Scale Factor
Place a **known physical weight** on a pad.  The scale factor is:

```
scale_factor = (raw_reading - tare_offset) / known_kg
```

To convert any future raw reading to kg:

```
weight_kg = (raw_reading - tare_offset) / scale_factor
```

### Persistence
Calibration values are currently held in memory.  To persist them, the `CalibrationStore._save()` and `_load()` stub methods should be replaced with JSON file I/O — the rest of the system stays unchanged.

---

## Data Flow (Hardware Path)

```
[Load cell] → [HX711 ADC] → [ESP32 GPIO] → [JSON over USB Serial]
           → [Python serial reader (future)] → [FastAPI backend]
           → [React dashboard]
```

The Serial JSON format (see `firmware/esp32_hx711/README.md`) was designed to map directly to the backend `HoofReading` model.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, Pydantic v2 |
| Frontend | React 18, TypeScript, Vite |
| Firmware | Arduino / ESP32 C++ |
| Testing | pytest |

---

## Limitations and Future Work

- Calibration is in-memory only; add JSON/SQLite persistence for field use.
- No authentication — add API keys or local-only binding for any deployment.
- A `serial_reader.py` bridge module is needed to stream live ESP32 data into the backend.
- Load cell temperature compensation is not yet implemented.
- The stability thresholds are initial estimates; tune after real horse trials.
