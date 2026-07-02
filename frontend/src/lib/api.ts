/**
 * api.ts — Typed API client for the EquiTare backend.
 *
 * All fetch calls are centralised here so the rest of the app
 * only imports these functions — easy to mock in tests, easy to swap
 * the base URL for production.
 */

import type { HoofReading, CalibrationState, SessionInfo, SimulateMode } from "./types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

/** Generic helper: fetch JSON and throw on non-2xx responses. */
async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }
  return response.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Readings
// ---------------------------------------------------------------------------

/** GET /api/readings/latest — returns null if no reading exists yet. */
export async function getLatestReading(): Promise<HoofReading | null> {
  return apiFetch<HoofReading | null>("/api/readings/latest");
}

/** POST /api/readings/simulate — generate and return a new reading. */
export async function simulateReading(mode: SimulateMode = "stable"): Promise<HoofReading> {
  return apiFetch<HoofReading>("/api/readings/simulate", {
    method: "POST",
    body: JSON.stringify({ mode }),
  });
}

// ---------------------------------------------------------------------------
// Calibration
// ---------------------------------------------------------------------------

/** POST /api/calibration/tare — zero all pads. */
export async function tare(): Promise<void> {
  await apiFetch<unknown>("/api/calibration/tare", { method: "POST", body: "{}" });
}

/** POST /api/calibration/set-known-load */
export async function setKnownLoad(pad: string, knownKg: number): Promise<void> {
  await apiFetch<unknown>("/api/calibration/set-known-load", {
    method: "POST",
    body: JSON.stringify({ pad, known_kg: knownKg }),
  });
}

/** GET /api/calibration */
export async function getCalibration(): Promise<CalibrationState> {
  return apiFetch<CalibrationState>("/api/calibration");
}

// ---------------------------------------------------------------------------
// Sessions
// ---------------------------------------------------------------------------

/** POST /api/session/start */
export async function startSession(): Promise<SessionInfo> {
  return apiFetch<SessionInfo>("/api/session/start", { method: "POST", body: "{}" });
}

/** POST /api/session/stop */
export async function stopSession(): Promise<SessionInfo> {
  return apiFetch<SessionInfo>("/api/session/stop", { method: "POST", body: "{}" });
}

/** GET /api/session/current */
export async function getCurrentSession(): Promise<SessionInfo | null> {
  return apiFetch<SessionInfo | null>("/api/session/current");
}

/** GET /api/session/history */
export async function getSessionHistory(): Promise<SessionInfo[]> {
  return apiFetch<SessionInfo[]>("/api/session/history");
}
