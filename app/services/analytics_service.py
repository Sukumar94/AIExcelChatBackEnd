"""
Analytics service - performs data analysis and computations.
"""

from __future__ import annotations

import logging
from typing import Any

import polars as pl

from app.database.schema_manager import SchemaManager
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Provides analytical operations on workbook data."""

    def __init__(self) -> None:
        self.schema_manager = SchemaManager()

    def get_summary(self, session_id: str, sheet_name: str | None = None) -> dict[str, Any]:
        """Get a comprehensive summary of the data."""
        session, sheet_name, df = SessionService.get_sheet_dataframe(session_id, sheet_name)

        summary: dict[str, Any] = {
            "file_name": session.metadata.file_name,
            "sheet_name": sheet_name,
            "total_rows": df.height,
            "total_columns": df.width,
            "columns": [],
            "statistics": {},
        }

        for col in df.columns:
            col_info: dict[str, Any] = {
                "name": col,
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].null_count()),
                "null_percentage": round(df[col].null_count() / max(df.height, 1) * 100, 2),
                "unique_count": int(df[col].n_unique()),
            }

            # Numeric stats
            if df[col].dtype in (pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64):
                try:
                    col_info["min"] = float(df[col].min())
                    col_info["max"] = float(df[col].max())
                    col_info["mean"] = float(df[col].mean())
                    col_info["std"] = float(df[col].std())
                    col_info["median"] = float(df[col].median())
                except Exception:
                    pass

            # String stats
            elif df[col].dtype == pl.Utf8:
                try:
                    col_info["min_length"] = int(df[col].str.len_bytes().min())
                    col_info["max_length"] = int(df[col].str.len_bytes().max())
                except Exception:
                    pass

            summary["columns"].append(col_info)

        # DuckDB stats
        try:
            db_stats = self.schema_manager.get_sheet_stats(session_id, sheet_name)
            summary["statistics"] = db_stats
        except Exception as e:
            logger.warning("Failed to get DB stats: %s", e)

        return summary

    def get_column_analysis(self, session_id: str, column: str, sheet_name: str | None = None) -> dict[str, Any]:
        """Get detailed analysis of a specific column."""
        _, sheet_name, df = SessionService.get_sheet_dataframe(session_id, sheet_name)

        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in sheet '{sheet_name}'")

        series = df[column]
        analysis: dict[str, Any] = {
            "column": column,
            "dtype": str(series.dtype),
            "count": int(series.len()),
            "null_count": int(series.null_count()),
            "unique_count": int(series.n_unique()),
        }

        if series.dtype in (pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64):
            analysis.update({
                "min": float(series.min()),
                "max": float(series.max()),
                "mean": float(series.mean()),
                "std": float(series.std()),
                "median": float(series.median()),
                "q1": float(series.quantile(0.25)),
                "q3": float(series.quantile(0.75)),
            })

        return analysis

    def detect_outliers(self, session_id: str, column: str, sheet_name: str | None = None) -> list[dict[str, Any]]:
        """Detect outliers in a numeric column using IQR method."""
        _, sheet_name, df = SessionService.get_sheet_dataframe(session_id, sheet_name)

        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found")

        series = df[column].drop_nulls()
        if series.dtype not in (pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64):
            raise ValueError(f"Column '{column}' is not numeric")

        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = df.filter(
            (pl.col(column) < lower) | (pl.col(column) > upper)
        ).select([pl.all()]).head(100)

        return {
            "column": column,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "lower_bound": lower,
            "upper_bound": upper,
            "outlier_count": outliers.height,
            "outliers": outliers.to_dicts() if outliers.height > 0 else [],
        }