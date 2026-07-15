"""
Recommendation tool - suggests analyses and visualizations.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from app.services.session_service import SessionService
from app.tools.base_tool import BaseTool


class RecommendationTool(BaseTool):
    """Tool for recommending analyses."""

    @property
    def name(self) -> str:
        return "recommend_analysis"

    @property
    def description(self) -> str:
        return "Recommend analyses and visualizations based on data structure. Parameters: session_id, sheet_name (optional)"

    def execute(self, session_id: str, sheet_name: str | None = None, **kwargs: Any) -> dict[str, Any]:
        _, actual_sheet, df = SessionService.get_sheet_dataframe(session_id, sheet_name)

        recommendations = []
        numeric_cols = [c for c in df.columns if df[c].dtype in (
            pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64
        )]
        categorical_cols = [c for c in df.columns if df[c].dtype == pl.Utf8]
        date_cols = [c for c in df.columns if df[c].dtype == pl.Date]

        if numeric_cols and categorical_cols:
            recommendations.append({
                "type": "chart",
                "suggestion": f"Bar chart of {numeric_cols[0]} by {categorical_cols[0]}",
                "chart_type": "bar",
                "x_axis": categorical_cols[0],
                "y_axis": numeric_cols[0],
            })

        if len(numeric_cols) >= 2:
            recommendations.append({
                "type": "chart",
                "suggestion": f"Scatter plot of {numeric_cols[0]} vs {numeric_cols[1]}",
                "chart_type": "scatter",
                "x_axis": numeric_cols[0],
                "y_axis": numeric_cols[1],
            })

        if date_cols and numeric_cols:
            recommendations.append({
                "type": "chart",
                "suggestion": f"Line chart of {numeric_cols[0]} over time ({date_cols[0]})",
                "chart_type": "line",
                "x_axis": date_cols[0],
                "y_axis": numeric_cols[0],
            })

        if numeric_cols:
            recommendations.append({
                "type": "analysis",
                "suggestion": f"Statistical summary of all numeric columns",
                "action": "summary",
            })
            recommendations.append({
                "type": "analysis",
                "suggestion": f"Detect outliers in {numeric_cols[0]}",
                "action": "outliers",
                "column": numeric_cols[0],
            })

        return {
            "sheet_name": actual_sheet,
            "recommendations": recommendations,
        }