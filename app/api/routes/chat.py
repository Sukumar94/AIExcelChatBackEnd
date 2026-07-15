"""
Chat routes - ask questions about uploaded workbooks.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_chat_service, get_metadata_store
from app.schemas.chat import ChatHistoryResponse, ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.database.metadata_store import MetadataStore

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chat"],
)


@router.post("", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    """Ask a natural language question about an uploaded workbook."""
    try:
        if not request.session_id or not request.question:
            raise HTTPException(status_code=400, detail="session_id and question are required")
        
        result = chat_service.ask(
            session_id=request.session_id,
            question=request.question,
            sheet_name=request.sheet_name,
        )
        return ChatResponse(
            answer=result.get("answer", ""),
            sql_query=result.get("sql_query"),
            chart_config=result.get("chart_config"),
            sources=result.get("sources"),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat processing failed",
        )


@router.get("/history/{session_id}", response_model=list[ChatHistoryResponse])
async def get_chat_history(
    session_id: str,
    metadata_store: MetadataStore = Depends(get_metadata_store),
):
    """Get chat history for a session."""
    try:
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required")
        history = metadata_store.get_chat_history(session_id)
        return [
            ChatHistoryResponse(
                id=h["id"],
                question=h["question"],
                answer=h["answer"],
                sql_query=h.get("sql_query"),
                chart_config=h.get("chart_config"),
                created_at=str(h["created_at"]),
            )
            for h in history
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history",
        )