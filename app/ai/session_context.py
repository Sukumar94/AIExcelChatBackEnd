"""
Session context management for AI interactions.
"""

from __future__ import annotations

from typing import Any

from app.ai.memory import ConversationMemory
from app.services.session_service import SessionService


class SessionContext:
    """Manages AI-related context for each session."""

    def __init__(self) -> None:
        self.memory = ConversationMemory()

    def get_context(self, session_id: str) -> dict[str, Any]:
        """Get full context for AI processing."""
        session = SessionService.get_session(session_id)
        if session is None:
            return {}

        return {
            "session_id": session_id,
            "file_name": session.metadata.file_name,
            "total_sheets": session.metadata.total_sheets,
            "sheets": list(session.sheets.keys()),
            "conversation_history": self.memory.get_formatted_context(session_id),
        }

    def add_user_message(self, session_id: str, message: str) -> None:
        """Record a user message."""
        self.memory.add_message(session_id, "user", message)

    def add_assistant_message(self, session_id: str, message: str) -> None:
        """Record an assistant message."""
        self.memory.add_message(session_id, "assistant", message)