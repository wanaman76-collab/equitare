/**
 * types.ts — Shared TypeScript type definitions for EquiTare.
 *
 * These mirror the Pydantic models in the backend.  If you add fields to
 * the backend models, update these types too.
 */

/** A single hoof measurement snapshot. */
export interface HoofReading {
  timestamp: string;   // ISO 8601 UTC string
  fl_kg: number;
  fr_kg: number;
  rl_kg: number;
  rr_kg: number;
  total_kg: number;
  left_kg: number;
  right_kg: number;
  front_kg: number;
  rear_kg: number;
  left_percent: number;
  right_percent: number;
  front_percent: number;
  rear_percent: number;
  is_stable: boolean;
  stability_reason: string;
}

/** Calibration state returned by GET /api/calibration */
export interface CalibrationState {
  tare_offsets: Record<string, number>;
  scale_factors: Record<string, number>;
}

/** Session info returned by session endpoints */
export interface SessionInfo {
  session_id: string;
  started_at: string;
  stopped_at: string | null;
  readings: HoofReading[];
  is_active: boolean;
}

/** Simulation mode used in POST /api/readings/simulate */
export type SimulateMode = "stable" | "unstable";
