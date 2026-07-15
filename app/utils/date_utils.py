"""
Date utility functions.
"""

from __future__ import annotations

from datetime import datetime, timezone


def now_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def format_timestamp(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object."""
    return dt.strftime(fmt)