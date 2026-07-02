/**
 * App.tsx — Root component for the EquiTare dashboard.
 *
 * Layout:
 *   - Header with project name
 *   - Simulate reading button (stable / unstable)
 *   - LiveReadingPanel: FL/FR/RL/RR values
 *   - BalanceSummary: total weight, stability, left/right, front/rear
 *   - SessionControls: start/stop session
 *   - CalibrationPanel: tare and known-load calibration
 */

import { useState, useCallback } from "react";
import { simulateReading } from "./lib/api";
import type { HoofReading, SessionInfo, SimulateMode } from "./lib/types";
import { LiveReadingPanel } from "./components/LiveReadingPanel";
import { BalanceSummary } from "./components/BalanceSummary";
import { CalibrationPanel } from "./components/CalibrationPanel";
import { SessionControls } from "./components/SessionControls";

const headerStyle: React.CSSProperties = {
  background: "#1a1a2e",
  color: "#fff",
  padding: "16px 24px",
  marginBottom: 24,
};

const containerStyle: React.CSSProperties = {
  maxWidth: 700,
  margin: "0 auto",
  padding: "0 16px",
  fontFamily: "system-ui, sans-serif",
};

const cardStyle: React.CSSProperties = {
  background: "#fff",
  border: "1px solid #e0e0e0",
  borderRadius: 8,
  padding: 20,
  marginBottom: 16,
  boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
};

function App() {
  const [reading, setReading] = useState<HoofReading | null>(null);
  const [session, setSession] = useState<SessionInfo | null>(null);
  const [simMode, setSimMode] = useState<SimulateMode>("stable");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const handleSimulate = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await simulateReading(simMode);
      setReading(result);
    } catch (err) {
      setError(`Failed to generate reading: ${err}`);
    } finally {
      setLoading(false);
    }
  }, [simMode]);

  return (
    <>
      {/* Header */}
      <header style={headerStyle}>
        <h1 style={{ margin: 0, fontSize: 24 }}>🐴 EquiTare</h1>
        <p style={{ margin: "4px 0 0", fontSize: 13, color: "#aaa" }}>
          Distributed Hoof Weight Measurement System — R&amp;D Prototype
        </p>
      </header>

      <div style={containerStyle}>
        {/* Simulate controls */}
        <div style={cardStyle}>
          <h2 style={{ marginTop: 0 }}>Simulator</h2>
          <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            <label style={{ fontSize: 14 }}>
              Mode:{" "}
              <select
                value={simMode}
                onChange={(e) => setSimMode(e.target.value as SimulateMode)}
                style={{ padding: "5px 10px", borderRadius: 4, border: "1px solid #ccc", fontSize: 14 }}
              >
                <option value="stable">Stable</option>
                <option value="unstable">Unstable</option>
              </select>
            </label>
            <button
              onClick={handleSimulate}
              disabled={loading}
              style={{
                padding: "8px 20px",
                borderRadius: 4,
                border: "none",
                background: "#4a90d9",
                color: "#fff",
                fontWeight: "bold",
                fontSize: 14,
                cursor: loading ? "not-allowed" : "pointer",
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? "Generating…" : "Generate Simulated Reading"}
            </button>
          </div>
          {error && <p style={{ color: "#c0392b", fontSize: 13, marginTop: 8 }}>{error}</p>}
          <p style={{ fontSize: 12, color: "#888", marginTop: 8, marginBottom: 0 }}>
            <strong>Stable mode</strong>: gentle drift, all pads loaded.{" "}
            <strong>Unstable mode</strong>: random spikes / unloaded pads.
          </p>
        </div>

        {/* Live readings */}
        <div style={cardStyle}>
          <LiveReadingPanel reading={reading} />
        </div>

        {/* Balance summary */}
        <div style={cardStyle}>
          <BalanceSummary reading={reading} />
        </div>

        {/* Session controls */}
        <div style={cardStyle}>
          <SessionControls session={session} onSessionChange={setSession} />
        </div>

        {/* Calibration */}
        <div style={cardStyle}>
          <CalibrationPanel />
        </div>

        <footer style={{ textAlign: "center", color: "#bbb", fontSize: 12, padding: "20px 0" }}>
          EquiTare v0.1.0 — Engineering R&amp;D Prototype
        </footer>
      </div>
    </>
  );
}

export default App;
