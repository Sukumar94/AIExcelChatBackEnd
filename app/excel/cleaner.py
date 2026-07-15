"""
Data cleaning utilities for Excel data.
"""

from __future__ import annotations

import logging

import polars as pl

logger = logging.getLogger(__name__)


class DataCleaner:
    """Cleans and normalizes DataFrame content."""

    @staticmethod
    def clean_dataframe(df: pl.DataFrame) -> pl.DataFrame:
        """Apply standard cleaning operations."""
        df = DataCleaner._strip_whitespace(df)
        df = DataCleaner._convert_dates(df)
        df = DataCleaner._convert_numeric(df)
        return df

    @staticmethod
    def _strip_whitespace(df: pl.DataFrame) -> pl.DataFrame:
        """Strip whitespace from string columns."""
        str_cols = [c for c in df.columns if df[c].dtype == pl.Utf8]
        if not str_cols:
            return df
        return df.with_columns(
            [pl.col(c).str.strip_chars().alias(c) for c in str_cols]
        )

    @staticmethod
    def _convert_dates(df: pl.DataFrame) -> pl.DataFrame:
        """Auto-detect and convert date-like string columns."""
        for col in df.columns:
            if df[col].dtype != pl.Utf8:
                continue
            sample = df[col].drop_nulls().head(10)
            if sample.len() == 0:
                continue
            # Check if looks like a date
            first_val = str(sample[0])
            if any(sep in first_val for sep in ["-", "/"]) and len(first_val) >= 8:
                try:
                    df = df.with_columns(
                        pl.col(col).str.to_date(format="%Y-%m-%d", strict=False)
                        .fill_null(pl.col(col).str.to_date(format="%d/%m/%Y", strict=False))
                        .fill_null(pl.col(col).str.to_date(format="%m/%d/%Y", strict=False))
                        .alias(col)
                    )
                except Exception:
                    pass
        return df

    @staticmethod
    def _convert_numeric(df: pl.DataFrame) -> pl.DataFrame:
        """Auto-convert string columns that look numeric."""
        for col in df.columns:
            if df[col].dtype != pl.Utf8:
                continue
            try:
                numeric = df[col].str.replace(",", "").str.replace("$", "").str.replace("€", "").str.replace("£", "")
                parsed = numeric.cast(pl.Float64, strict=False)
                if parsed.null_count() < df[col].null_count() + (df[col].len() * 0.3):  # at least 70% parseable
                    df = df.with_columns(parsed.alias(col))
            except Exception:
                pass
        return df