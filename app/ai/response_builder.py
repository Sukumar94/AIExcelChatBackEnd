"""
Response builder - formats AI responses for the API.
"""

from __future__ import annotations

from typing import Any


class ResponseBuilder:
    """Builds structured responses from AI processing results."""

    @staticmethod
    def build_chat_response(
        answer: str,
        sql_query: str | None = None,
        chart_config: dict[str, Any] | None = None,
        sources: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build a standardized chat response."""
        return {
            "answer": answer,
            "sql_query": sql_query,
            "chart_config": chart_config,
            "sources": sources or [],
        }

    @staticmethod
    def build_error_response(error: str) -> dict[str, Any]:
        """Build an error response."""
        return {
            "answer": f"I encountered an error: {error}",
            "sql_query": None,
            "chart_config": None,
            "sources": [],
        }