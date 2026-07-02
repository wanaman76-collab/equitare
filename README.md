# EquiTare 🐴

**Distributed Hoof Weight Measurement System — Engineering R&D Prototype**

EquiTare uses four low-profile hoof pads (FL, FR, RL, RR) to estimate total horse weight and front/rear and left/right weight distribution — without a single large weighing platform.

> ⚠️ This is a student/internship R&D prototype. It is **not** a certified veterinary instrument or commercial scale.

---

## Repository Structure

```
equitare/
  README.md
  backend/              Python FastAPI backend
    app/
      main.py           API endpoints
      models.py         Pydantic data models
      calculations.py   Weight distribution calculations
      calibration.py    Per-pad tare + scale factor management
      simulator.py      Realistic horse weight simulator
      session_store.py  In-memory measurement session store
    tests/
      test_calculations.py
      test_calibration.py
    requirements.txt
  frontend/             React + TypeScript dashboard (Vite)
    src/
      App.tsx
      components/
        LiveReadingPanel.tsx
        BalanceSummary.tsx
        CalibrationPanel.tsx
        SessionControls.tsx
      lib/
        api.ts          Typed API client
        types.ts        Shared TypeScript types
  firmware/
    esp32_hx711/        Arduino sketch for ESP32 + 4× HX711
      esp32_hx711.ino
      README.md
  docs/
    system_overview.md  Architecture and design notes
    sample_payloads.md  Example API requests/responses
```

---

## Quick Start

### 1. Backend (FastAPI)

**Requirements:** Python 3.11+

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

### 2. Frontend (React + Vite)

**Requirements:** Node.js 18+

```bash
cd frontend
npm install
npm run dev
```

The dashboard will open at `http://localhost:5173`.

> The Vite dev server proxies `/api` requests to `http://localhost:8000`, so
> make sure the backend is running first.

### 3. Running Tests

```bash
cd backend
pytest tests/ -v
```

All tests are self-contained and do not require a running server.

---

## How the Simulator Works

The backend includes a built-in horse weight simulator so you can develop and test
without any physical hardware.

**Stable mode** generates readings with gentle drift across the four pads,
mimicking a horse standing quietly.  All pads stay above the minimum threshold
and total variation is low — stability checks pass.

**Unstable mode** randomly introduces either a near-zero pad (horse lifting a hoof)
or a sudden spike on one pad — stability checks fail, which is the expected behaviour.

To generate a simulated reading, send:

```bash
curl -X POST http://localhost:8000/api/readings/simulate \
     -H "Content-Type: application/json" \
     -d '{"mode": "stable"}'
```

Or click the **"Generate Simulated Reading"** button in the dashboard.

---

## API Overview

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| GET | `/api/readings/latest` | Get the most recent reading |
| POST | `/api/readings/simulate` | Generate a simulated reading |
| POST | `/api/calibration/tare` | Zero all pad offsets |
| POST | `/api/calibration/set-known-load` | Set scale factor from known weight |
| GET | `/api/calibration` | Get current calibration state |
| POST | `/api/session/start` | Start a measurement session |
| POST | `/api/session/stop` | Stop the current session |
| GET | `/api/session/current` | Get the active session |
| GET | `/api/session/history` | List completed sessions |

Full interactive documentation: `http://localhost:8000/docs`
See `docs/sample_payloads.md` for example requests and responses.

---

## ESP32 Hardware Integration (Future)

The firmware in `firmware/esp32_hx711/` is a ready-to-upload Arduino sketch for:
- ESP32 development board
- 4× HX711 ADC modules, one per hoof pad

The sketch outputs one JSON line per reading (~10 Hz) over USB Serial:

```json
{"timestamp_ms":12345,"fl_raw":100200,"fr_raw":102400,"rl_raw":98100,"rr_raw":99300,"fl_kg":110.5,"fr_kg":112.0,"rl_kg":105.2,"rr_kg":108.8}
```

**Integration path:**
1. Flash the sketch to the ESP32.
2. Connect via USB to the host running the backend.
3. A future `serial_reader.py` module reads the JSON stream using `pyserial`,
   calls `calculate_totals()` and `check_stability()`, and posts readings to the backend.
4. The React dashboard updates in real time — **no changes needed to the frontend or API**.

See `firmware/esp32_hx711/README.md` for full wiring, calibration, and upload instructions.

---

## Calibration

1. **Tare:** With no load on the pads, call `POST /api/calibration/tare`.
   This records the current sensor output as the zero point.
2. **Known load:** Place a known weight on one pad, then call
   `POST /api/calibration/set-known-load` with the pad name and weight in kg.
   The backend calculates the scale factor automatically.

Calibration is currently in-memory. To persist it across restarts, the
`CalibrationStore._save()` and `_load()` stub methods in `calibration.py`
should be replaced with JSON file I/O.

---

## Further Reading

- `docs/system_overview.md` — Architecture, calculations, stability logic
- `docs/sample_payloads.md` — Example API payloads
- `firmware/esp32_hx711/README.md` — Hardware setup and calibration procedure

