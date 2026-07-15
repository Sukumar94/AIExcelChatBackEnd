"""
Query planner - determines the best approach to answer a question.
"""

from __future__ import annotations

import logging
from typing import Any

from app.ai.llm import LLMService

logger = logging.getLogger(__name__)


class QueryPlanner:
    """
    Analyzes a question and determines the best strategy to answer it.
    """

    def __init__(self) -> None:
        self.llm = LLMService()

    def plan(self, question: str, schema_context: str) -> dict[str, Any]:
        """
        Analyze the question and return a plan.
        Returns: {
            "needs_sql": bool,
            "needs_chart": bool,
            "intent": str,
            "explanation": str
        }
        """
        prompt = f"""Analyze this user question about their Excel data and determine the best approach.

Question: {question}

Data Schema:
{schema_context}

Respond with JSON only:
{{
    "needs_sql": true/false,
    "needs_chart": true/false,
    "intent": "summary|analysis|comparison|trend|distribution|general",
    "explanation": "brief explanation of the approach"
}}"""
        try:
            result = self.llm.extract_json(prompt)
            return {
                "needs_sql": result.get("needs_sql", False),
                "needs_chart": result.get("needs_chart", False),
                "intent": result.get("intent", "general"),
                "explanation": result.get("explanation", ""),
            }
        except Exception as e:
            logger.warning("Query planning failed: %s", e)
            return {
                "needs_sql": True,
                "needs_chart": False,
                "intent": "general",
                "explanation": "Defaulting to SQL-based analysis.",
            }