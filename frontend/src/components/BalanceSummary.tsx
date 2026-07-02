/**
 * BalanceSummary.tsx — Shows total weight, left/right and front/rear balance,
 * and the stability status of the current reading.
 */

import type { HoofReading } from "../lib/types";

interface Props {
  reading: HoofReading | null;
}

/** A simple horizontal progress bar. */
function BalanceBar({
  leftLabel,
  leftPct,
  rightLabel,
}: {
  leftLabel: string;
  leftPct: number;
  rightLabel: string;
}) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div
        style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 2 }}
      >
        <span>
          {leftLabel} ({leftPct.toFixed(1)}%)
        </span>
        <span>
          {rightLabel} ({(100 - leftPct).toFixed(1)}%)
        </span>
      </div>
      <div
        style={{
          height: 16,
          borderRadius: 8,
          background: "#e0e0e0",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${leftPct}%`,
            background: "#4a90d9",
            borderRadius: "8px 0 0 8px",
            transition: "width 0.3s ease",
          }}
        />
      </div>
    </div>
  );
}

export function BalanceSummary({ reading }: Props) {
  if (!reading) {
    return (
      <section style={{ marginBottom: 24 }}>
        <h2 style={{ marginBottom: 8 }}>Weight Summary</h2>
        <p style={{ color: "#aaa", fontSize: 14 }}>Awaiting first reading…</p>
      </section>
    );
  }

  const isStableColor = reading.is_stable ? "#2ecc71" : "#e74c3c";

  return (
    <section style={{ marginBottom: 24 }}>
      <h2 style={{ marginBottom: 12 }}>Weight Summary</h2>

      {/* Total weight */}
      <div style={{ marginBottom: 16 }}>
        <span style={{ fontSize: 14, color: "#555" }}>Total estimated weight: </span>
        <span style={{ fontSize: 24, fontWeight: "bold" }}>{reading.total_kg.toFixed(1)} kg</span>
      </div>

      {/* Stability indicator */}
      <div
        style={{
          display: "inline-block",
          padding: "4px 12px",
          borderRadius: 20,
          background: isStableColor,
          color: "#fff",
          fontWeight: "bold",
          fontSize: 13,
          marginBottom: 16,
        }}
      >
        {reading.is_stable ? "✓ STABLE" : "✗ UNSTABLE"}
      </div>
      <p style={{ fontSize: 12, color: "#666", marginTop: 4, marginBottom: 16 }}>
        {reading.stability_reason}
      </p>

      {/* Balance bars */}
      <BalanceBar
        leftLabel="Left"
        leftPct={reading.left_percent}
        rightLabel="Right"
      />
      <BalanceBar
        leftLabel="Front"
        leftPct={reading.front_percent}
        rightLabel="Rear"
      />
    </section>
  );
}
