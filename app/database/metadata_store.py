"""
Metadata store for tracking uploaded workbooks and their schemas.
Uses DuckDB for persistence.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.database.connection import DatabaseManager

logger = logging.getLogger(__name__)


class MetadataStore:
    """Persistent metadata storage using DuckDB."""

    _initialized = False

    def __init__(self) -> None:
        self.db = DatabaseManager()
        if not MetadataStore._initialized:
            self._ensure_tables()
            MetadataStore._initialized = True

    def _ensure_tables(self) -> None:
        """Create metadata tables/indexes if they don't exist."""
        # Keep table creation idempotent to avoid expensive DDL on hot paths
        # and to preserve metadata across service restarts.
        self.db.execute("CREATE SEQUENCE IF NOT EXISTS chat_history_seq START 1")
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS workbook_metadata (
                session_id VARCHAR PRIMARY KEY,
                file_name VARCHAR NOT NULL,
                file_size BIGINT,
                sheet_count INTEGER,
                sheets_info JSON,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY,
                session_id VARCHAR NOT NULL,
                question VARCHAR NOT NULL,
                answer VARCHAR NOT NULL,
                sql_query VARCHAR,
                chart_config JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.execute(
            "CREATE INDEX IF NOT EXISTS idx_chat_history_session_created "
            "ON chat_history(session_id, created_at)"
        )
        self.db.execute(
            "CREATE INDEX IF NOT EXISTS idx_workbook_metadata_last_accessed "
            "ON workbook_metadata(last_accessed)"
        )

    def save_workbook_metadata(
        self,
        session_id: str,
        file_name: str,
        file_size: int,
        sheet_count: int,
        sheets_info: list[dict[str, Any]],
    ) -> None:
        """Save workbook metadata after upload."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.db.execute(
            """
            INSERT INTO workbook_metadata (session_id, file_name, file_size, sheet_count, sheets_info, uploaded_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (session_id) DO UPDATE SET
                file_name = EXCLUDED.file_name,
                file_size = EXCLUDED.file_size,
                sheet_count = EXCLUDED.sheet_count,
                sheets_info = EXCLUDED.sheets_info,
                last_accessed = EXCLUDED.last_accessed
            """,
            [session_id, file_name, file_size, sheet_count, json.dumps(sheets_info), now, now],
        )
        logger.info("Saved metadata for session %s", session_id)

    def get_workbook_metadata(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve workbook metadata."""
        result = self.db.execute(
            "SELECT * FROM workbook_metadata WHERE session_id = ?", [session_id]
        ).pl()
        if result.height == 0:
            return None
        row = result.to_dicts()[0]
        row["sheets_info"] = json.loads(row["sheets_info"]) if row.get("sheets_info") else []
        return row

    def update_last_accessed(self, session_id: str) -> None:
        """Update the last_accessed timestamp."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.db.execute(
            "UPDATE workbook_metadata SET last_accessed = ? WHERE session_id = ?",
            [now, session_id],
        )

    def save_chat_message(
        self,
        session_id: str,
        question: str,
        answer: str,
        sql_query: str | None = None,
        chart_config: dict[str, Any] | None = None,
    ) -> int:
        """Save a chat message and return its ID."""
        self.db.execute(
            """
            INSERT INTO chat_history (id, session_id, question, answer, sql_query, chart_config)
            VALUES (nextval('chat_history_seq'), ?, ?, ?, ?, ?)
            """,
            [
                session_id,
                question,
                answer,
                sql_query,
                json.dumps(chart_config) if chart_config else None,
            ],
        )
        result = self.db.execute("SELECT currval('chat_history_seq')").fetchone()
        return result[0]

    def get_chat_history(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Get chat history for a session."""
        result = self.db.execute(
            """
            SELECT id, question, answer, sql_query, chart_config, created_at
            FROM chat_history
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            [session_id, limit],
        ).pl()
        rows = result.to_dicts()
        for row in rows:
            if row.get("chart_config"):
                row["chart_config"] = json.loads(row["chart_config"])
        return rows

    def list_sessions(self, limit: int = 20) -> list[dict[str, Any]]:
        """List recent workbook sessions."""
        result = self.db.execute(
            """
            SELECT session_id, file_name, sheet_count, uploaded_at, last_accessed
            FROM workbook_metadata
            ORDER BY last_accessed DESC
            LIMIT ?
            """,
            [limit],
        ).pl()
        return result.to_dicts()

    def delete_session(self, session_id: str) -> None:
        """Delete a session and its chat history."""
        self.db.execute("DELETE FROM workbook_metadata WHERE session_id = ?", [session_id])
        self.db.execute("DELETE FROM chat_history WHERE session_id = ?", [session_id])
        logger.info("Deleted session %s", session_id)