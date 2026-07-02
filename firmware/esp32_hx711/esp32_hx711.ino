/*
 * esp32_hx711.ino — EquiTare firmware skeleton for ESP32 + 4× HX711 load cells
 *
 * Hardware assumed:
 *   - ESP32 development board
 *   - 4× HX711 ADC modules, one per hoof pad (FL, FR, RL, RR)
 *   - Each HX711 connected to a dedicated pair of GPIO pins (DOUT + SCK)
 *
 * This sketch:
 *   1. Initialises four HX711 modules.
 *   2. Reads raw values from each module at ~5–10 Hz.
 *   3. Applies per-pad tare offsets and scale factors to convert raw → kg.
 *   4. Outputs a JSON string over the hardware Serial port.
 *   5. Accepts simple Serial commands (TARE, PRINT_CALIBRATION, SET_FACTOR).
 *
 * Serial output example (one line per reading):
 *   {"timestamp_ms":12345,"fl_raw":100000,"fr_raw":102000,
 *    "rl_raw":98000,"rr_raw":99000,
 *    "fl_kg":110.5,"fr_kg":112.0,"rl_kg":105.2,"rr_kg":108.8}
 *
 * NOTE: This is a skeleton / prototype.  The HX711 library calls are
 * placeholders until the real library is wired in (e.g. bogde/HX711 or
 * olkal/HX711_ADC).  See README.md in this folder for integration notes.
 *
 * Author:  EquiTare project team
 * Version: 0.1.0
 */

// ---------------------------------------------------------------------------
// Pin definitions — adjust for your actual wiring
// ---------------------------------------------------------------------------

// HX711 DOUT (data) and SCK (clock) pin pairs
#define FL_DOUT  4
#define FL_SCK   5

#define FR_DOUT  16
#define FR_SCK   17

#define RL_DOUT  18
#define RL_SCK   19

#define RR_DOUT  21
#define RR_SCK   22

// ---------------------------------------------------------------------------
// Calibration values (in-memory, replace with EEPROM/NVS later if desired)
// ---------------------------------------------------------------------------

// Tare offsets: raw counts when no load is on each pad
long tare_fl = 0L;
long tare_fr = 0L;
long tare_rl = 0L;
long tare_rr = 0L;

// Scale factors: raw counts per 1 kg
// These are placeholder values — run a known-load calibration on real hardware.
float scale_fl = 1000.0f;
float scale_fr = 1000.0f;
float scale_rl = 1000.0f;
float scale_rr = 1000.0f;

// ---------------------------------------------------------------------------
// Reading interval
// ---------------------------------------------------------------------------
const unsigned long READ_INTERVAL_MS = 100;  // ~10 Hz
unsigned long last_read_ms = 0;

// ---------------------------------------------------------------------------
// HX711 stub — replace with real library calls
// ---------------------------------------------------------------------------

/*
 * To use the bogde/HX711 library, add:
 *
 *   #include <HX711.h>
 *   HX711 scale_fl_obj, scale_fr_obj, scale_rl_obj, scale_rr_obj;
 *
 * and in setup():
 *   scale_fl_obj.begin(FL_DOUT, FL_SCK);
 *   ...
 *
 * Then replace read_raw_*() calls below with scale_fl_obj.read_average(3).
 */

long read_raw_fl() {
  // STUB: replace with actual HX711 read for FL
  return tare_fl + (long)(random(-200, 200));
}

long read_raw_fr() {
  return tare_fr + (long)(random(-200, 200));
}

long read_raw_rl() {
  return tare_rl + (long)(random(-200, 200));
}

long read_raw_rr() {
  return tare_rr + (long)(random(-200, 200));
}

// ---------------------------------------------------------------------------
// Conversion helper
// ---------------------------------------------------------------------------

float raw_to_kg(long raw, long tare_offset, float factor) {
  if (factor == 0.0f) return 0.0f;
  return (float)(raw - tare_offset) / factor;
}

// ---------------------------------------------------------------------------
// Serial command handler
// ---------------------------------------------------------------------------

void handle_serial_command(const String& cmd) {
  if (cmd == "TARE") {
    tare_fl = read_raw_fl();
    tare_fr = read_raw_fr();
    tare_rl = read_raw_rl();
    tare_rr = read_raw_rr();
    Serial.println("{\"cmd\":\"TARE\",\"status\":\"OK\"}");

  } else if (cmd == "PRINT_CALIBRATION") {
    Serial.print("{\"tare_fl\":");  Serial.print(tare_fl);
    Serial.print(",\"tare_fr\":");  Serial.print(tare_fr);
    Serial.print(",\"tare_rl\":");  Serial.print(tare_rl);
    Serial.print(",\"tare_rr\":");  Serial.print(tare_rr);
    Serial.print(",\"scale_fl\":"); Serial.print(scale_fl, 4);
    Serial.print(",\"scale_fr\":"); Serial.print(scale_fr, 4);
    Serial.print(",\"scale_rl\":"); Serial.print(scale_rl, 4);
    Serial.print(",\"scale_rr\":"); Serial.print(scale_rr, 4);
    Serial.println("}");

  } else if (cmd.startsWith("SET_FACTOR ")) {
    // Expected format: SET_FACTOR FL 1234.56
    String rest = cmd.substring(11);  // after "SET_FACTOR "
    int space = rest.indexOf(' ');
    if (space < 0) {
      Serial.println("{\"error\":\"SET_FACTOR: missing value\"}");
      return;
    }
    String pad = rest.substring(0, space);
    float val  = rest.substring(space + 1).toFloat();

    if      (pad == "FL") { scale_fl = val; }
    else if (pad == "FR") { scale_fr = val; }
    else if (pad == "RL") { scale_rl = val; }
    else if (pad == "RR") { scale_rr = val; }
    else {
      Serial.println("{\"error\":\"Unknown pad. Use FL/FR/RL/RR\"}");
      return;
    }
    Serial.print("{\"cmd\":\"SET_FACTOR\",\"pad\":\"");
    Serial.print(pad);
    Serial.print("\",\"factor\":");
    Serial.print(val, 4);
    Serial.println("}");

  } else {
    Serial.print("{\"error\":\"Unknown command: ");
    Serial.print(cmd);
    Serial.println("\"}");
  }
}

// ---------------------------------------------------------------------------
// Setup and main loop
// ---------------------------------------------------------------------------

void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); }

  Serial.println("{\"msg\":\"EquiTare firmware v0.1.0 starting\"}");

  // TODO: initialise real HX711 objects here
  // scale_fl_obj.begin(FL_DOUT, FL_SCK);
  // ...

  // Seed the RNG (used only by the stub functions above)
  randomSeed(analogRead(0));

  // Perform an initial tare so the first readings start from zero
  tare_fl = read_raw_fl();
  tare_fr = read_raw_fr();
  tare_rl = read_raw_rl();
  tare_rr = read_raw_rr();

  Serial.println("{\"msg\":\"Initial tare complete. Ready.\"}");
}

void loop() {
  // --- Handle incoming Serial commands ---
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.length() > 0) {
      handle_serial_command(cmd);
    }
  }

  // --- Periodic sensor reading and JSON output ---
  unsigned long now = millis();
  if (now - last_read_ms >= READ_INTERVAL_MS) {
    last_read_ms = now;

    long raw_fl = read_raw_fl();
    long raw_fr = read_raw_fr();
    long raw_rl = read_raw_rl();
    long raw_rr = read_raw_rr();

    float kg_fl = raw_to_kg(raw_fl, tare_fl, scale_fl);
    float kg_fr = raw_to_kg(raw_fr, tare_fr, scale_fr);
    float kg_rl = raw_to_kg(raw_rl, tare_rl, scale_rl);
    float kg_rr = raw_to_kg(raw_rr, tare_rr, scale_rr);

    // Output one JSON line per reading
    Serial.print("{");
    Serial.print("\"timestamp_ms\":");  Serial.print(now);
    Serial.print(",\"fl_raw\":");       Serial.print(raw_fl);
    Serial.print(",\"fr_raw\":");       Serial.print(raw_fr);
    Serial.print(",\"rl_raw\":");       Serial.print(raw_rl);
    Serial.print(",\"rr_raw\":");       Serial.print(raw_rr);
    Serial.print(",\"fl_kg\":");        Serial.print(kg_fl, 2);
    Serial.print(",\"fr_kg\":");        Serial.print(kg_fr, 2);
    Serial.print(",\"rl_kg\":");        Serial.print(kg_rl, 2);
    Serial.print(",\"rr_kg\":");        Serial.print(kg_rr, 2);
    Serial.println("}");
  }
}
