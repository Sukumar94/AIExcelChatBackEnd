"""
Dashboard tool - provides dashboard data.
"""

from __future__ import annotations

from typing import Any

from app.services.dashboard_service import DashboardService
from app.tools.base_tool import BaseTool


class DashboardTool(BaseTool):
    """Tool for dashboard data."""

    def __init__(self) -> None:
        self.dashboard_service = DashboardService()

    @property
    def name(self) -> str:
        return "get_dashboard"

    @property
    def description(self) -> str:
        return "Get dashboard data for a session. Parameters: session_id"

    def execute(self, session_id: str, **kwargs: Any) -> dict[str, Any]:
        return self.dashboard_service.get_dashboard_data(session_id)