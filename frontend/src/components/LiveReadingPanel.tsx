/**
 * LiveReadingPanel.tsx — Shows the four individual hoof pad readings.
 *
 * Displays FL, FR, RL, RR weights in a 2×2 grid that mirrors the physical
 * pad layout when viewed from above the horse.
 */

import type { HoofReading } from "../lib/types";

interface Props {
  reading: HoofReading | null;
}

const padStyle: React.CSSProperties = {
  border: "2px solid #ccc",
  borderRadius: 8,
  padding: "12px 16px",
  textAlign: "center",
  minWidth: 100,
  background: "#f9f9f9",
};

const labelStyle: React.CSSProperties = {
  fontSize: 12,
  color: "#666",
  marginBottom: 4,
};

const valueStyle: React.CSSProperties = {
  fontSize: 28,
  fontWeight: "bold",
  color: "#1a1a2e",
};

const unitStyle: React.CSSProperties = {
  fontSize: 12,
  color: "#999",
};

function PadCell({ label, kg }: { label: string; kg: number | undefined }) {
  return (
    <div style={padStyle}>
      <div style={labelStyle}>{label}</div>
      <div style={valueStyle}>{kg !== undefined ? kg.toFixed(1) : "—"}</div>
      <div style={unitStyle}>kg</div>
    </div>
  );
}

export function LiveReadingPanel({ reading }: Props) {
  return (
    <section style={{ marginBottom: 24 }}>
      <h2 style={{ marginBottom: 12 }}>Live Hoof Readings</h2>

      {/* 2×2 grid mirroring the pad layout: FL|FR on top, RL|RR on bottom */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 12,
          maxWidth: 280,
        }}
      >
        <PadCell label="FL (Front-Left)" kg={reading?.fl_kg} />
        <PadCell label="FR (Front-Right)" kg={reading?.fr_kg} />
        <PadCell label="RL (Rear-Left)" kg={reading?.rl_kg} />
        <PadCell label="RR (Rear-Right)" kg={reading?.rr_kg} />
      </div>

      {reading && (
        <p style={{ marginTop: 12, color: "#555", fontSize: 14 }}>
          Last updated: {new Date(reading.timestamp).toLocaleTimeString()}
        </p>
      )}

      {!reading && (
        <p style={{ color: "#aaa", marginTop: 12, fontSize: 14 }}>
          No reading yet — click "Generate Simulated Reading" below.
        </p>
      )}
    </section>
  );
}
