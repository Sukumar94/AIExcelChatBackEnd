"""
Audio utility functions for voice processing.
"""

from __future__ import annotations


def validate_audio_format(filename: str) -> bool:
    """Check if the audio file format is supported."""
    supported = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return f".{ext}" in supported