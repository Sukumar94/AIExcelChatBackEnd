"""
Report tool - generates reports.
"""

from __future__ import annotations

from typing import Any

from app.services.report_service import ReportService
from app.tools.base_tool import BaseTool


class ReportTool(BaseTool):
    """Tool for generating reports."""

    def __init__(self) -> None:
        self.report_service = ReportService()

    @property
    def name(self) -> str:
        return "generate_report"

    @property
    def description(self) -> str:
        return "Generate a report from workbook data. Parameters: session_id, sheet_name (optional), include_charts (bool)"

    def execute(self, session_id: str, sheet_name: str | None = None, include_charts: bool = True, **kwargs: Any) -> dict[str, Any]:
        return self.report_service.generate_report(session_id, sheet_name, include_charts)