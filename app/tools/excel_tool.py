"""
Excel tool - provides Excel data access to the AI agent.
"""

from __future__ import annotations

from typing import Any

from app.services.session_service import SessionService
from app.tools.base_tool import BaseTool


class ExcelTool(BaseTool):
    """Tool for accessing Excel workbook data."""

    @property
    def name(self) -> str:
        return "excel_data"

    @property
    def description(self) -> str:
        return "Get data from an uploaded Excel workbook. Parameters: session_id, sheet_name (optional)"

    def execute(self, session_id: str, sheet_name: str | None = None, **kwargs: Any) -> dict[str, Any]:
        session, actual_sheet, df = SessionService.get_sheet_dataframe(session_id, sheet_name)
        return {
            "file_name": session.metadata.file_name,
            "sheet_name": actual_sheet,
            "rows": df.height,
            "columns": df.width,
            "column_names": df.columns,
            "preview": df.head(5).to_dicts(),
        }