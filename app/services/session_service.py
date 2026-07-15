"""
Session management service.
Uses in-memory storage with DuckDB persistence fallback.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from threading import Lock

from app.core.settings import settings
from app.models.session import SessionModel

logger = logging.getLogger(__name__)


class SessionService:
    """
    Thread-safe in-memory session manager.
    Sessions are stored in memory for fast access and persisted to DuckDB.
    """

    _sessions: dict[str, SessionModel] = {}
    _lock = Lock()

    @classmethod
    def create_session(cls, session: SessionModel) -> SessionModel:
        """Store a new session."""
        with cls._lock:
            cls._sessions[session.session_id] = session
        logger.info("Session created: %s (%s)", session.session_id[:8], session.metadata.file_name)
        return session

    @classmethod
    def get_session(cls, session_id: str) -> SessionModel | None:
        """Retrieve a session by ID."""
        return cls._sessions.get(session_id)

    @classmethod
    def get_sheet_dataframe(cls, session_id: str, sheet_name: str | None = None) -> tuple[SessionModel, str, any]:
        """
        Get a session and optionally a specific sheet's DataFrame.
        Returns (session, sheet_name, dataframe).
        """
        session = cls.get_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")

        if sheet_name is None:
            # Use the first sheet
            sheet_name = next(iter(session.sheets.keys()))

        if sheet_name not in session.sheets:
            raise ValueError(f"Sheet '{sheet_name}' not found in session {session_id}")

        return session, sheet_name, session.sheets[sheet_name].dataframe

    @classmethod
    def delete_session(cls, session_id: str) -> bool:
        """Remove a session."""
        with cls._lock:
            result = cls._sessions.pop(session_id, None) is not None
        if result:
            logger.info("Session deleted: %s", session_id[:8])
        return result

    @classmethod
    def session_exists(cls, session_id: str) -> bool:
        """Check if a session exists."""
        return session_id in cls._sessions

    @classmethod
    def total_sessions(cls) -> int:
        """Number of active sessions."""
        return len(cls._sessions)

    @classmethod
    def clear(cls) -> None:
        """Remove all sessions."""
        with cls._lock:
            cls._sessions.clear()
        logger.info("All sessions cleared")

    @classmethod
    def cleanup_expired_sessions(cls) -> int:
        """Remove sessions older than TTL. Returns count of deleted sessions."""
        cutoff = datetime.now() - timedelta(minutes=settings.session_ttl_minutes)
        expired = []
        
        with cls._lock:
            for sid, session in list(cls._sessions.items()):
                if session.metadata.uploaded_at < cutoff:
                    expired.append(sid)
                    del cls._sessions[sid]
        
        if expired:
            logger.info("Cleaned up %d expired sessions", len(expired))
        return len(expired)

    @classmethod
    def get_active_session_count(cls) -> int:
        """Get count of active sessions."""
        return len(cls._sessions)