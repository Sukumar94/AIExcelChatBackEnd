"""
Application-wide logging configuration.
"""

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """Configure root logger with structured format."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers on reload
    if not root.handlers:
        root.addHandler(handler)

    # Quiet noisy libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("faiss").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Convenience helper."""
    return logging.getLogger(name)