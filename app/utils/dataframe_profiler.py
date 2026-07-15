"""
DataFrame profiling utilities.
"""

from __future__ import annotations

from typing import Any

import polars as pl


class DataFrameProfiler:
    """Profiles a DataFrame to extract useful metadata."""

    @staticmethod
    def profile(df: pl.DataFrame) -> dict[str, Any]:
        """Generate a profile of the DataFrame."""
        return {
            "rows": df.height,
            "columns": df.width,
            "column_details": [
                {
                    "name": col,
                    "dtype": str(df[col].dtype),
                    "null_count": int(df[col].null_count()),
                    "null_pct": round(df[col].null_count() / max(df.height, 1) * 100, 2),
                    "unique_count": int(df[col].n_unique()),
                    "is_numeric": df[col].dtype in (pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64),
                    "is_string": df[col].dtype == pl.Utf8,
                }
                for col in df.columns
            ],
            "estimated_memory_mb": round(df.estimated_size("mb"), 2),
        }