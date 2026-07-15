"""
Extracts metadata from Excel DataFrames.
"""

from __future__ import annotations

from typing import Any

import polars as pl


class MetadataExtractor:
    """Extracts structural metadata from DataFrames."""

    @staticmethod
    def extract_sheet_info(sheet_name: str, df: pl.DataFrame) -> dict[str, Any]:
        """Extract metadata for a single sheet."""
        info: dict[str, Any] = {
            "sheet_name": sheet_name,
            "rows": df.height,
            "columns": df.width,
            "column_names": df.columns,
            "column_types": [str(dtype) for dtype in df.dtypes],
            "null_counts": {col: int(df[col].null_count()) for col in df.columns},
            "unique_counts": {},
            "sample_data": {},
        }

        # Sample data (first 3 rows)
        if df.height > 0:
            head = df.head(3)
            info["sample_data"] = {
                col: [str(v) if v is not None else None for v in head[col].to_list()]
                for col in df.columns
            }

        # Unique counts for first 10 columns (to avoid heavy computation)
        for col in df.columns[:10]:
            try:
                info["unique_counts"][col] = df[col].n_unique()
            except Exception:
                info["unique_counts"][col] = 0

        return info

    @staticmethod
    def extract_all_sheets(sheets: dict[str, pl.DataFrame]) -> list[dict[str, Any]]:
        """Extract metadata for all sheets."""
        return [
            MetadataExtractor.extract_sheet_info(name, df)
            for name, df in sheets.items()
        ]