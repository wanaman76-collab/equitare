/**
 * SessionControls.tsx — Start and stop measurement sessions.
 *
 * Displays the current session status and reading count,
 * and provides buttons to start/stop a session.
 */

import { useState } from "react";
import { startSession, stopSession, getCurrentSession } from "../lib/api";
import type { SessionInfo } from "../lib/types";

interface Props {
  session: SessionInfo | null;
  onSessionChange: (session: SessionInfo | null) => void;
}

const buttonStyle: React.CSSProperties = {
  padding: "8px 16px",
  borderRadius: 4,
  border: "none",
  cursor: "pointer",
  fontWeight: "bold",
  fontSize: 14,
  marginRight: 10,
};

export function SessionControls({ session, onSessionChange }: Props) {
  const [error, setError] = useState<string>("");

  async function handleStart() {
    setError("");
    try {
      const newSession = await startSession();
      onSessionChange(newSession);
    } catch (err) {
      setError(`Could not start session: ${err}`);
    }
  }

  async function handleStop() {
    setError("");
    try {
      await stopSession();
      onSessionChange(null);
    } catch (err) {
      setError(`Could not stop session: ${err}`);
    }
  }

  return (
    <section style={{ marginBottom: 24 }}>
      <h2 style={{ marginBottom: 12 }}>Session</h2>

      {session ? (
        <div style={{ marginBottom: 12 }}>
          <span
            style={{
              display: "inline-block",
              padding: "3px 10px",
              borderRadius: 12,
              background: "#2ecc71",
              color: "#fff",
              fontSize: 12,
              fontWeight: "bold",
              marginRight: 10,
            }}
          >
            ACTIVE
          </span>
          <span style={{ fontSize: 14, color: "#444" }}>
            Session <code>{session.session_id.slice(0, 8)}…</code> started at{" "}
            {new Date(session.started_at).toLocaleTimeString()}
            {" · "}
            {session.readings.length} reading(s)
          </span>
        </div>
      ) : (
        <p style={{ color: "#999", fontSize: 14, marginBottom: 12 }}>No active session.</p>
      )}

      <div>
        <button
          style={{ ...buttonStyle, background: "#27ae60", color: "#fff" }}
          onClick={handleStart}
          disabled={!!session}
        >
          Start Session
        </button>
        <button
          style={{ ...buttonStyle, background: "#c0392b", color: "#fff" }}
          onClick={handleStop}
          disabled={!session}
        >
          Stop Session
        </button>
      </div>

      {error && <p style={{ color: "#c0392b", fontSize: 13, marginTop: 8 }}>{error}</p>}
    </section>
  );
}
