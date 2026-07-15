"""
Chart utility functions.
"""

from __future__ import annotations

from typing import Any

import plotly.express as px


def get_chart_types() -> list[str]:
    """Get list of supported chart types."""
    return ["bar", "line", "pie", "scatter", "histogram", "box", "heatmap"]


def get_default_colors() -> list[str]:
    """Get default color sequence."""
    return px.colors.qualitative.Plotly