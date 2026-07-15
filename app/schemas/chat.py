"""
Chat-related request/response schemas.
"""

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request to ask a question about a workbook."""

    session_id: str = Field(..., description="Session ID of the uploaded workbook")
    question: str = Field(..., description="Natural language question about the data")
    sheet_name: str | None = Field(default=None, description="Specific sheet to query (optional)")


class ChatResponse(BaseModel):
    """Response from the AI chatbot."""

    answer: str = Field(..., description="AI-generated answer")
    sql_query: str | None = Field(default=None, description="SQL query used (if any)")
    chart_config: dict[str, Any] | None = Field(default=None, description="Chart configuration if chart was generated")
    sources: list[str] | None = Field(default=None, description="Source sheets referenced")


class ChatHistoryResponse(BaseModel):
    """Chat history entry."""

    id: int
    question: str
    answer: str
    sql_query: str | None = None
    chart_config: dict[str, Any] | None = None
    created_at: str