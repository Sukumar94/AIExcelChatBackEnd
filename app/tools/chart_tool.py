"""
Chart tool - generates charts from data.
"""

from __future__ import annotations

from typing import Any

from app.models.chart import ChartConfig
from app.services.chart_service import ChartService
from app.tools.base_tool import BaseTool


class ChartTool(BaseTool):
    """Tool for generating charts."""

    def __init__(self) -> None:
        self.chart_service = ChartService()

    @property
    def name(self) -> str:
        return "generate_chart"

    @property
    def description(self) -> str:
        return "Generate a chart from workbook data. Parameters: session_id, chart_type, title, x_axis, y_axis, sheet_name (optional)"

    def execute(self, session_id: str, chart_type: str, title: str, x_axis: str, y_axis: str | None = None, sheet_name: str | None = None, **kwargs: Any) -> dict[str, Any]:
        config = ChartConfig(
            chart_type=chart_type,
            title=title,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        response = self.chart_service.generate_chart(session_id, config, sheet_name)
        return response.model_dump()