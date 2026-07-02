"""
session_store.py — In-memory session management for EquiTare.

A "session" is a named measurement run.  You start one, collect readings,
then stop it.  Previous sessions are kept in memory so you can review them.

This module uses a simple list-based store.  If persistence is needed later,
swap the in-memory list for database calls — the rest of the API layer stays
the same.
"""

import uuid
from datetime import datetime
from typing import Optional

from app.models import HoofReading, SessionInfo


class SessionStore:
    """
    Manages a single active session and a history of completed sessions.
    """

    def __init__(self):
        self._active: Optional[SessionInfo] = None
        self._history: list[SessionInfo] = []

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def start_session(self) -> SessionInfo:
        """
        Begin a new measurement session.

        Raises:
            RuntimeError: If a session is already active.
        """
        if self._active is not None:
            raise RuntimeError("A session is already active. Stop it before starting a new one.")

        session = SessionInfo(
            session_id=str(uuid.uuid4()),
            started_at=datetime.utcnow(),
        )
        self._active = session
        return session

    def stop_session(self) -> SessionInfo:
        """
        End the currently active session and move it to history.

        Raises:
            RuntimeError: If no session is active.
        """
        if self._active is None:
            raise RuntimeError("No active session to stop.")

        self._active.stopped_at = datetime.utcnow()
        self._active.is_active = False
        self._history.append(self._active)
        finished = self._active
        self._active = None
        return finished

    # ------------------------------------------------------------------
    # Reading management
    # ------------------------------------------------------------------

    def add_reading(self, reading: HoofReading) -> None:
        """
        Append a reading to the active session.

        Note: Readings are added regardless of stability — the caller decides
        whether to filter by is_stable before calling this.
        """
        if self._active is None:
            # Not in a session; silently discard (or raise, depending on desired behaviour)
            return
        self._active.readings.append(reading)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def current_session(self) -> Optional[SessionInfo]:
        """Return the currently active session, or None."""
        return self._active

    def session_history(self) -> list[SessionInfo]:
        """Return all completed sessions (oldest first)."""
        return list(self._history)


# Module-level singleton
session_store = SessionStore()
