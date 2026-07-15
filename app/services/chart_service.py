"""
Chart service - generates charts from workbook data.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import plotly.express as px
import plotly.graph_objects as go
import polars as pl

from app.models.chart import ChartConfig, ChartResponse
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)


class ChartService:
    """Generates interactive charts using Plotly."""

    def generate_chart(
        self,
        session_id: str,
        config: ChartConfig,
        sheet_name: str | None = None,
    ) -> ChartResponse:
        """Generate a chart based on configuration."""
        _, sheet_name, df = SessionService.get_sheet_dataframe(session_id, sheet_name)

        fig = self._create_figure(df, config)
        chart_json = json.loads(fig.to_json())

        # Generate insights
        insights = self._generate_insights(df, config)

        return ChartResponse(
            chart_json=chart_json,
            chart_type=config.chart_type,
            title=config.title,
            insights=insights,
        )

    def _create_figure(self, df: pl.DataFrame, config: ChartConfig) -> go.Figure:
        """Create a Plotly figure based on config."""
        pdf = df.to_pandas()

        if config.chart_type == "bar":
            fig = px.bar(
                pdf, x=config.x_axis, y=config.y_axis,
                color=config.color, title=config.title,
            )
        elif config.chart_type == "line":
            fig = px.line(
                pdf, x=config.x_axis, y=config.y_axis,
                color=config.color, title=config.title,
            )
        elif config.chart_type == "pie":
            fig = px.pie(
                pdf, names=config.x_axis, values=config.y_axis,
                title=config.title,
            )
        elif config.chart_type == "scatter":
            fig = px.scatter(
                pdf, x=config.x_axis, y=config.y_axis,
                color=config.color, title=config.title,
            )
        elif config.chart_type == "histogram":
            fig = px.histogram(
                pdf, x=config.x_axis, color=config.color,
                title=config.title,
            )
        elif config.chart_type == "box":
            fig = px.box(
                pdf, x=config.x_axis, y=config.y_axis,
                color=config.color, title=config.title,
            )
        elif config.chart_type == "heatmap":
            fig = px.density_heatmap(
                pdf, x=config.x_axis, y=config.y_axis,
                title=config.title,
            )
        else:
            fig = px.bar(pdf, x=config.x_axis, y=config.y_axis, title=config.title)

        fig.update_layout(
            template="plotly_white",
            width=config.width,
            height=config.height,
        )
        return fig

    def auto_chart(
        self,
        session_id: str,
        sheet_name: str | None = None,
    ) -> list[ChartResponse]:
        """Auto-generate recommended charts for the data."""
        _, sheet_name, df = SessionService.get_sheet_dataframe(session_id, sheet_name)

        charts = []
        numeric_cols = [c for c in df.columns if df[c].dtype in (
            pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64
        )]
        categorical_cols = [c for c in df.columns if df[c].dtype == pl.Utf8]

        if numeric_cols and categorical_cols:
            # Bar chart: first categorical vs first numeric
            config = ChartConfig(
                chart_type="bar",
                title=f"{numeric_cols[0]} by {categorical_cols[0]}",
                x_axis=categorical_cols[0],
                y_axis=numeric_cols[0],
            )
            charts.append(self.generate_chart(session_id, config, sheet_name))

        if len(numeric_cols) >= 2:
            # Scatter: first two numeric columns
            config = ChartConfig(
                chart_type="scatter",
                title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
                x_axis=numeric_cols[0],
                y_axis=numeric_cols[1],
            )
            charts.append(self.generate_chart(session_id, config, sheet_name))

        if numeric_cols:
            # Histogram of first numeric column
            config = ChartConfig(
                chart_type="histogram",
                title=f"Distribution of {numeric_cols[0]}",
                x_axis=numeric_cols[0],
            )
            charts.append(self.generate_chart(session_id, config, sheet_name))

        if categorical_cols:
            # Pie chart of first categorical
            config = ChartConfig(
                chart_type="pie",
                title=f"Distribution of {categorical_cols[0]}",
                x_axis=categorical_cols[0],
            )
            charts.append(self.generate_chart(session_id, config, sheet_name))

        return charts

    def _generate_insights(self, df: pl.DataFrame, config: ChartConfig) -> str:
        """Generate text insights about the chart."""
        insights = []
        if config.x_axis and config.x_axis in df.columns:
            insights.append(f"X-axis: {config.x_axis} ({df[config.x_axis].n_unique()} unique values)")
        if config.y_axis:
            y_cols = [config.y_axis] if isinstance(config.y_axis, str) else config.y_axis
            for y in y_cols:
                if y in df.columns and df[y].dtype in (pl.Float32, pl.Float64, pl.Int32, pl.Int64):
                    insights.append(f"{y}: min={df[y].min():.2f}, max={df[y].max():.2f}, avg={df[y].mean():.2f}")
        return " | ".join(insights) if insights else "Chart generated successfully."