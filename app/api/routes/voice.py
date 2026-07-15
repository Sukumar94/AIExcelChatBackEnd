"""
Voice query routes.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_voice_service
from app.schemas.voice import VoiceQueryRequest, VoiceQueryResponse
from app.services.voice_service import VoiceService

router = APIRouter(
    prefix="/api/v1/voice",
    tags=["Voice"],
)


@router.post("", response_model=VoiceQueryResponse)
async def voice_query(
    request: VoiceQueryRequest,
    voice_service: VoiceService = Depends(get_voice_service),
):
    """Process a voice query against a workbook."""
    try:
        return voice_service.process_voice_query(
            session_id=request.session_id,
            transcribed_text=request.text,
            sheet_name=request.sheet_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))