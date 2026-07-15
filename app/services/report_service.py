"""
Report service - generates HTML/PDF reports from workbook data.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from app.services.analytics_service import AnalyticsService
from app.services.chart_service import ChartService
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)


class ReportService:
    """Generates reports from workbook data."""

    def __init__(self) -> None:
        self.analytics = AnalyticsService()
        self.chart_service = ChartService()

    def generate_report(
        self,
        session_id: str,
        sheet_name: str | None = None,
        include_charts: bool = True,
    ) -> dict[str, Any]:
        """Generate a comprehensive report."""
        session = SessionService.get_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")

        if sheet_name is None:
            sheet_name = next(iter(session.sheets.keys()))

        # Get summary
        summary = self.analytics.get_summary(session_id, sheet_name)

        # Generate charts
        charts = []
        if include_charts:
            try:
                charts = self.chart_service.auto_chart(session_id, sheet_name)
            except Exception as e:
                logger.warning("Chart generation failed: %s", e)

        # Build HTML report
        html = self._build_html_report(session, sheet_name, summary, charts)

        return {
            "report_html": html,
            "insights": self._extract_insights(summary),
            "charts": [c.model_dump() for c in charts],
            "statistics": summary,
        }

    def _build_html_report(
        self,
        session: Any,
        sheet_name: str,
        summary: dict[str, Any],
        charts: list[Any],
    ) -> str:
        """Build an HTML report string."""
        cols_html = ""
        for col in summary.get("columns", []):
            stats_html = ""
            if "mean" in col:
                stats_html = f"""
                <div class="stats">
                    <span>Min: {col.get('min', 'N/A'):.2f}</span>
                    <span>Max: {col.get('max', 'N/A'):.2f}</span>
                    <span>Mean: {col.get('mean', 'N/A'):.2f}</span>
                    <span>Nulls: {col.get('null_count', 0)}</span>
                </div>
                """
            cols_html += f"""
            <div class="column-card">
                <h3>{col['name']}</h3>
                <p>Type: {col['dtype']} | Unique: {col.get('unique_count', 'N/A')}</p>
                {stats_html}
            </div>
            """

        charts_html = ""
        for c in charts:
            charts_html += f"""
            <div class="chart-container">
                <h3>{c.title}</h3>
                <div id="chart-{c.chart_type}"></div>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Report - {session.metadata.file_name}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
                h1 {{ color: #1a73e8; }}
                .summary {{ background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                .column-card {{ background: white; border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 4px; }}
                .stats {{ display: flex; gap: 15px; font-size: 0.9em; color: #666; }}
                .chart-container {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Data Report: {session.metadata.file_name}</h1>
            <div class="summary">
                <h2>Sheet: {sheet_name}</h2>
                <p>Rows: {summary.get('total_rows', 0)} | Columns: {summary.get('total_columns', 0)}</p>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <h2>Column Analysis</h2>
            {cols_html}
            <h2>Charts</h2>
            {charts_html}
        </body>
        </html>
        """

    def _extract_insights(self, summary: dict[str, Any]) -> list[str]:
        """Extract text insights from summary data."""
        insights = []
        for col in summary.get("columns", []):
            if col.get("null_percentage", 0) > 50:
                insights.append(f"Column '{col['name']}' has {col['null_percentage']:.0f}% missing values.")
            if "mean" in col:
                insights.append(f"Average of '{col['name']}': {col['mean']:.2f}")
        return insights