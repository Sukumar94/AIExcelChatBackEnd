"""
Conversation memory management.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any


class ConversationMemory:
    """
    Stores recent conversation history per session.
    Used to provide context to the LLM.
    """

    def __init__(self, max_history: int = 10) -> None:
        self.max_history = max_history
        self._histories: dict[str, deque[dict[str, str]]] = defaultdict(
            lambda: deque(maxlen=max_history)
        )

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self._histories[session_id].append({
            "role": role,
            "content": content,
        })

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        """Get the conversation history for a session."""
        return list(self._histories.get(session_id, []))

    def clear(self, session_id: str) -> None:
        """Clear history for a session."""
        self._histories.pop(session_id, None)

    def get_formatted_context(self, session_id: str) -> str:
        """Get history formatted as a string for LLM prompts."""
        history = self.get_history(session_id)
        if not history:
            return ""
        parts = []
        for msg in history[-5:]:  # Last 5 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            parts.append(f"{role}: {msg['content']}")
        return "\n".join(parts)