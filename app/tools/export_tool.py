"""
Export tool - exports data in various formats.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import polars as pl

from app.services.session_service import SessionService
from app.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class ExportTool(BaseTool):
    """Tool for exporting data."""

    @property
    def name(self) -> str:
        return "export_data"

    @property
    def description(self) -> str:
        return "Export workbook data. Parameters: session_id, format (json/csv), sheet_name (optional)"

    def execute(self, session_id: str, format: str = "json", sheet_name: str | None = None, **kwargs: Any) -> dict[str, Any]:
        _, actual_sheet, df = SessionService.get_sheet_dataframe(session_id, sheet_name)

        if format == "json":
            data = df.to_dicts()
            return {"format": "json", "data": data, "row_count": len(data)}
        elif format == "csv":
            csv_str = df.write_csv()
            return {"format": "csv", "data": csv_str, "row_count": df.height}
        else:
            return {"error": f"Unsupported format: {format}"}