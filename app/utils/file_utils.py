"""
File utility functions.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def ensure_dir(path: str | Path) -> Path:
    """Ensure a directory exists and return the Path object."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def safe_filename(filename: str) -> str:
    """Create a safe filename by removing problematic characters."""
    safe = "".join(c for c in filename if c.isalnum() or c in "._- ")
    return safe.strip() or "unnamed"


def file_size_str(size_bytes: int) -> str:
    """Convert bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"