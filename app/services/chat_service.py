"""
Chat service - handles natural language questions about workbook data.
Uses LLM + SQL generation + RAG for accurate answers.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.ai.agent import AIAgent
from app.database.metadata_store import MetadataStore
from app.database.schema_manager import SchemaManager
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)


class ChatService:
    """Handles user questions against uploaded Excel workbooks."""

    def __init__(self) -> None:
        self.agent = AIAgent()
        self.schema_manager = SchemaManager()
        self.metadata_store = MetadataStore()
        self._schema_context_cache: dict[tuple[str, str], str] = {}
        self._response_cache: dict[tuple[str, str, str], dict[str, Any]] = {}

    def ask(self, session_id: str, question: str, sheet_name: str | None = None) -> dict[str, Any]:
        """
        Process a natural language question about the workbook.
        Returns answer with optional SQL and chart config.
        """
        session = SessionService.get_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")

        # Determine which sheet to use
        if sheet_name is None:
            sheet_name = next(iter(session.sheets.keys()))

        if sheet_name not in session.sheets:
            raise ValueError(f"Sheet '{sheet_name}' not found")

        sheet = session.sheets[sheet_name]

        # Fast path for repeated prompts in the same session/sheet.
        question_key = " ".join(question.lower().split())
        response_cache_key = (session_id, sheet_name, question_key)
        cached = self._response_cache.get(response_cache_key)
        if cached is not None:
            # Keep user-visible history behavior unchanged.
            self.metadata_store.save_chat_message(
                session_id=session_id,
                question=question,
                answer=cached.get("answer", ""),
                sql_query=cached.get("sql_query"),
                chart_config=cached.get("chart_config"),
            )
            self.metadata_store.update_last_accessed(session_id)
            return dict(cached)

        # Get schema info for context (cached per session/sheet)
        cache_key = (session_id, sheet_name)
        schema_context = self._schema_context_cache.get(cache_key)
        if schema_context is None:
            schema_context = self._build_schema_context(session_id, sheet_name, sheet)
            self._schema_context_cache[cache_key] = schema_context

        # Get chat history for context
        chat_history = self.metadata_store.get_chat_history(session_id, limit=5)

        # Process through AI agent
        result = self.agent.process(
            question=question,
            schema_context=schema_context,
            sheet_name=sheet_name,
            session_id=session_id,
            chat_history=chat_history,
        )

        # Save to chat history
        self.metadata_store.save_chat_message(
            session_id=session_id,
            question=question,
            answer=result.get("answer", ""),
            sql_query=result.get("sql_query"),
            chart_config=result.get("chart_config"),
        )

        # Cache final result for identical follow-up requests.
        self._response_cache[response_cache_key] = dict(result)

        # Update last accessed
        self.metadata_store.update_last_accessed(session_id)

        return result

    def _build_schema_context(self, session_id: str, sheet_name: str, sheet: Any) -> str:
        """Build a schema description for the LLM context.

        Uses bounded sampling to avoid full-column scans on every chat call.
        """
        sample_df = sheet.dataframe.head(2000)
        cols = []
        for col_name in sheet.column_names:
            dtype = str(sheet.dataframe[col_name].dtype)
            nulls = sample_df[col_name].null_count()
            unique = sample_df[col_name].drop_nulls().n_unique()
            sample_vals = sample_df[col_name].drop_nulls().head(3).to_list()
            sample_str = ", ".join(str(v) for v in sample_vals[:3])
            cols.append(
                f"  - {col_name} ({dtype}): ~{nulls} nulls, ~{unique} unique "
                f"(sampled up to 2000 rows). Samples: [{sample_str}]"
            )

        return f"""Sheet: {sheet_name}
Rows: {sheet.rows}
Columns: {sheet.columns}

Column Details:
{chr(10).join(cols)}

The data is available as a DuckDB view named: session_{session_id[:8]}_{sheet_name}
You can write SQL queries against this view.
"""