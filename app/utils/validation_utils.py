"""
Validation utility functions.
"""

from __future__ import annotations

from typing import Any


def validate_session_id(session_id: str) -> bool:
    """Validate that a session ID is well-formed."""
    if not session_id or len(session_id) < 8:
        return False
    return True


def validate_sheet_name(sheet_name: str) -> bool:
    """Validate sheet name."""
    if not sheet_name or len(sheet_name) > 255:
        return False
    return True