"""
Tool router - routes AI requests to appropriate tools.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.analytics_service import AnalyticsService
from app.services.chart_service import ChartService
from app.services.report_service import ReportService

logger = logging.getLogger(__name__)


class ToolRouter:
    """Routes AI requests to the appropriate service based on intent."""

    def __init__(self) -> None:
        self.analytics = AnalyticsService()
        self.chart_service = ChartService()
        self.report_service = ReportService()

    def route(self, intent: str, session_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """Route a request to the appropriate tool."""
        if intent == "summary":
            return self.analytics.get_summary(session_id, params.get("sheet_name"))
        elif intent == "column_analysis":
            return self.analytics.get_column_analysis(
                session_id, params["column"], params.get("sheet_name")
            )
        elif intent == "outliers":
            return self.analytics.detect_outliers(
                session_id, params["column"], params.get("sheet_name")
            )
        elif intent == "auto_chart":
            charts = self.chart_service.auto_chart(session_id, params.get("sheet_name"))
            return {"charts": [c.model_dump() for c in charts]}
        elif intent == "report":
            return self.report_service.generate_report(
                session_id, params.get("sheet_name"), params.get("include_charts", True)
            )
        else:
            return {"error": f"Unknown intent: {intent}"}