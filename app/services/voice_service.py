"""
Voice service - handles voice query processing.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)


class VoiceService:
    """Processes voice queries against workbook data."""

    def __init__(self) -> None:
        self.chat_service = ChatService()

    def process_voice_query(
        self,
        session_id: str,
        transcribed_text: str,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """Process a voice-transcribed query."""
        result = self.chat_service.ask(
            session_id=session_id,
            question=transcribed_text,
            sheet_name=sheet_name,
        )
        return {
            "answer": result.get("answer", ""),
            "transcribed_text": transcribed_text,
            "sql_query": result.get("sql_query"),
        }