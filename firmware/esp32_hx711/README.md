# ESP32 + HX711 Firmware — EquiTare

This folder contains the Arduino sketch for the EquiTare ESP32 hardware node.

## Hardware required

| Component | Qty | Notes |
|-----------|-----|-------|
| ESP32 dev board | 1 | Any 38-pin variant works |
| HX711 ADC module | 4 | One per hoof pad |
| Load cell (strain gauge) | 4 | Rated for horse weight (~150–200 kg each) |

Default wiring (adjust in `esp32_hx711.ino` if needed):

| Pad | HX711 DOUT | HX711 SCK |
|-----|-----------|-----------|
| FL  | GPIO 4    | GPIO 5    |
| FR  | GPIO 16   | GPIO 17   |
| RL  | GPIO 18   | GPIO 19   |
| RR  | GPIO 21   | GPIO 22   |

## Dependencies

Install via Arduino Library Manager:

- **HX711** by Bogdan Necula (`bogde/HX711`) — or use `olkal/HX711_ADC` for
  continuous non-blocking reads.

Once installed, replace the `read_raw_*()` stub functions in the sketch with
the real library calls (see comments in the `.ino` file).

## Uploading

1. Install Arduino IDE ≥ 2.0 and the **ESP32 board package**
   (Boards Manager → search "esp32" by Espressif).
2. Open `esp32_hx711.ino`.
3. Select your board: **Tools → Board → ESP32 Dev Module**.
4. Set the correct COM/USB port.
5. Click Upload.

## Serial output

At ~10 Hz the firmware outputs one JSON line per reading:

```json
{"timestamp_ms":12345,"fl_raw":100200,"fr_raw":102400,"rl_raw":98100,"rr_raw":99300,"fl_kg":110.5,"fr_kg":112.0,"rl_kg":105.2,"rr_kg":108.8}
```

Open **Tools → Serial Monitor** at **115200 baud** to see live output.

## Serial commands

Send commands via the Serial Monitor (with line ending set to "Newline"):

| Command | Effect |
|---------|--------|
| `TARE` | Zero all four pads (remove load first) |
| `PRINT_CALIBRATION` | Print current tare offsets and scale factors |
| `SET_FACTOR FL 1234.56` | Update scale factor for the FL pad |
| `SET_FACTOR FR 1234.56` | Update scale factor for the FR pad |
| `SET_FACTOR RL 1234.56` | Update scale factor for the RL pad |
| `SET_FACTOR RR 1234.56` | Update scale factor for the RR pad |

## Integrating with the Python backend

The Python backend can read the JSON stream from `/dev/ttyUSB0` (Linux) or
`COM3` (Windows) using `pyserial`, parse each line, apply calibration, and
push readings to the API.  A future `serial_reader.py` module will handle this
bridge — the JSON format above was designed to be easy to parse.

## Calibration procedure

1. With **no load** on any pad, send `TARE`.
2. Place a known weight (e.g. 20 kg) on one pad.
3. Read the raw value from the Serial output.
4. Calculate: `scale_factor = (raw - tare_offset) / known_kg`
5. Send `SET_FACTOR <PAD> <value>`.
6. Repeat for each pad.
7. Send `PRINT_CALIBRATION` to verify.
