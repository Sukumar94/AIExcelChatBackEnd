"""
Statistics tool - computes statistical summaries.
"""

from __future__ import annotations

from typing import Any

from app.services.analytics_service import AnalyticsService
from app.tools.base_tool import BaseTool


class StatisticsTool(BaseTool):
    """Tool for computing statistics."""

    def __init__(self) -> None:
        self.analytics = AnalyticsService()

    @property
    def name(self) -> str:
        return "compute_statistics"

    @property
    def description(self) -> str:
        return "Compute statistics for a workbook sheet. Parameters: session_id, sheet_name (optional)"

    def execute(self, session_id: str, sheet_name: str | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.analytics.get_summary(session_id, sheet_name)