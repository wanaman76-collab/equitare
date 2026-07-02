/**
 * CalibrationPanel.tsx — Simple UI for tare and known-load calibration.
 *
 * This panel lets you:
 *  - Tare all pads (zero the offsets)
 *  - Enter a known load for a specific pad to set its scale factor
 */

import { useState } from "react";
import { tare, setKnownLoad } from "../lib/api";

interface Props {
  onAction?: (message: string) => void;
}

const inputStyle: React.CSSProperties = {
  padding: "6px 10px",
  border: "1px solid #ccc",
  borderRadius: 4,
  fontSize: 14,
  width: 120,
};

const selectStyle: React.CSSProperties = {
  padding: "6px 10px",
  border: "1px solid #ccc",
  borderRadius: 4,
  fontSize: 14,
};

const buttonStyle: React.CSSProperties = {
  padding: "7px 14px",
  borderRadius: 4,
  border: "none",
  cursor: "pointer",
  fontSize: 14,
  fontWeight: "bold",
};

export function CalibrationPanel({ onAction }: Props) {
  const [pad, setPad] = useState<string>("FL");
  const [knownKg, setKnownKg] = useState<string>("");
  const [status, setStatus] = useState<string>("");

  async function handleTare() {
    try {
      await tare();
      const msg = "Tare applied to all pads.";
      setStatus(msg);
      onAction?.(msg);
    } catch (err) {
      setStatus(`Tare failed: ${err}`);
    }
  }

  async function handleSetKnownLoad() {
    const kg = parseFloat(knownKg);
    if (isNaN(kg) || kg <= 0) {
      setStatus("Please enter a valid positive weight in kg.");
      return;
    }
    try {
      await setKnownLoad(pad, kg);
      const msg = `Scale factor updated for ${pad} using ${kg} kg reference.`;
      setStatus(msg);
      onAction?.(msg);
    } catch (err) {
      setStatus(`Set-known-load failed: ${err}`);
    }
  }

  return (
    <section style={{ marginBottom: 24 }}>
      <h2 style={{ marginBottom: 12 }}>Calibration</h2>

      {/* Tare button */}
      <div style={{ marginBottom: 16 }}>
        <button
          style={{ ...buttonStyle, background: "#e67e22", color: "#fff" }}
          onClick={handleTare}
        >
          Tare All Pads
        </button>
        <span style={{ marginLeft: 10, fontSize: 13, color: "#666" }}>
          Zero all pad offsets (remove horse / load first)
        </span>
      </div>

      {/* Known-load calibration */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
        <select
          style={selectStyle}
          value={pad}
          onChange={(e) => setPad(e.target.value)}
        >
          <option value="FL">FL</option>
          <option value="FR">FR</option>
          <option value="RL">RL</option>
          <option value="RR">RR</option>
        </select>

        <input
          style={inputStyle}
          type="number"
          min="0.1"
          step="0.1"
          placeholder="Known kg"
          value={knownKg}
          onChange={(e) => setKnownKg(e.target.value)}
        />

        <button
          style={{ ...buttonStyle, background: "#8e44ad", color: "#fff" }}
          onClick={handleSetKnownLoad}
        >
          Set Known Load
        </button>
      </div>

      {status && (
        <p style={{ marginTop: 10, fontSize: 13, color: "#333" }}>{status}</p>
      )}
    </section>
  );
}
