"""
Data normalizer for consistent column naming and types.
"""

from __future__ import annotations

import re

import polars as pl


class DataNormalizer:
    """Normalizes column names and data types for consistency."""

    @staticmethod
    def normalize_column_names(df: pl.DataFrame) -> pl.DataFrame:
        """Convert column names to snake_case."""
        mapping = {}
        for col in df.columns:
            new_name = col.strip()
            new_name = re.sub(r"[^a-zA-Z0-9_]+", "_", new_name)
            new_name = re.sub(r"_+", "_", new_name)
            new_name = new_name.strip("_").lower()
            if not new_name:
                new_name = "column"
            # Ensure uniqueness
            base = new_name
            counter = 1
            while new_name in mapping.values():
                new_name = f"{base}_{counter}"
                counter += 1
            mapping[col] = new_name
        return df.rename(mapping)

    @staticmethod
    def normalize_dataframe(df: pl.DataFrame) -> pl.DataFrame:
        """Full normalization pipeline."""
        df = DataNormalizer.normalize_column_names(df)
        return df