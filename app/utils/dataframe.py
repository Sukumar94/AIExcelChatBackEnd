"""
DataFrame utility functions.
"""

from __future__ import annotations

import polars as pl


def dataframe_to_dicts(df: pl.DataFrame, limit: int | None = None) -> list[dict]:
    """Convert a Polars DataFrame to a list of dicts, with optional limit."""
    if limit is not None:
        df = df.head(limit)
    return df.to_dicts()


def get_numeric_columns(df: pl.DataFrame) -> list[str]:
    """Get names of numeric columns."""
    return [
        c for c in df.columns
        if df[c].dtype in (pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64)
    ]


def get_categorical_columns(df: pl.DataFrame) -> list[str]:
    """Get names of string/categorical columns."""
    return [c for c in df.columns if df[c].dtype == pl.Utf8]


def get_date_columns(df: pl.DataFrame) -> list[str]:
    """Get names of date columns."""
    return [c for c in df.columns if df[c].dtype == pl.Date]