"""
Voice-related request/response schemas.
"""

from pydantic import BaseModel, Field


class VoiceQueryRequest(BaseModel):
    """Request with transcribed voice text."""

    session_id: str = Field(...)
    text: str = Field(..., description="Transcribed speech text")
    sheet_name: str | None = Field(default=None)


class VoiceQueryResponse(BaseModel):
    """Response to a voice query."""

    answer: str
    transcribed_text: str
    sql_query: str | None = None