"""
Dashboard service - provides aggregated data for the frontend dashboard.
"""

from __future__ import annotations

import logging
from typing import Any

from app.database.metadata_store import MetadataStore
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)


class DashboardService:
    """Provides dashboard data."""

    def __init__(self) -> None:
        self.metadata_store = MetadataStore()

    def get_dashboard_data(self, session_id: str) -> dict[str, Any]:
        """Get all data needed for the dashboard view."""
        session = SessionService.get_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")

        sheets_overview = []
        for name, sheet in session.sheets.items():
            sheets_overview.append({
                "name": name,
                "rows": sheet.rows,
                "columns": sheet.columns,
                "column_names": sheet.column_names,
            })

        chat_history = self.metadata_store.get_chat_history(session_id, limit=10)

        return {
            "session_id": session_id,
            "file_name": session.metadata.file_name,
            "uploaded_at": session.metadata.uploaded_at.isoformat(),
            "total_sheets": session.metadata.total_sheets,
            "sheets": sheets_overview,
            "recent_chats": chat_history,
        }

    def list_recent_sessions(self, limit: int = 10) -> list[dict[str, Any]]:
        """List recent sessions."""
        return self.metadata_store.list_sessions(limit=limit)