"""
Voice tool - processes voice queries.
"""

from __future__ import annotations

from typing import Any

from app.services.voice_service import VoiceService
from app.tools.base_tool import BaseTool


class VoiceTool(BaseTool):
    """Tool for voice query processing."""

    def __init__(self) -> None:
        self.voice_service = VoiceService()

    @property
    def name(self) -> str:
        return "process_voice"

    @property
    def description(self) -> str:
        return "Process a voice query. Parameters: session_id, text, sheet_name (optional)"

    def execute(self, session_id: str, text: str, sheet_name: str | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.voice_service.process_voice_query(session_id, text, sheet_name)