"""
Base tool class for the AI agent tool system.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract base class for all tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for the LLM."""

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with given parameters."""