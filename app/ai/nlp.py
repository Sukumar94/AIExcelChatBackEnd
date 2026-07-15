"""
NLP utilities for text processing.
"""

from __future__ import annotations

import re
from typing import Any


class NLPUtils:
    """Natural language processing utilities."""

    @staticmethod
    def extract_keywords(text: str) -> list[str]:
        """Extract important keywords from a question."""
        stop_words = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "above",
            "below", "between", "out", "off", "over", "under", "again",
            "further", "then", "once", "here", "there", "when", "where",
            "why", "how", "all", "each", "every", "both", "few", "more",
            "most", "other", "some", "such", "no", "nor", "not", "only",
            "own", "same", "so", "than", "too", "very", "just", "because",
            "and", "but", "or", "if", "while", "about", "up",
        }
        words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]

    @staticmethod
    def detect_question_type(question: str) -> str:
        """Detect the type of question being asked."""
        q_lower = question.lower().strip()

        if q_lower.startswith(("how many", "how much", "count")):
            return "count"
        elif q_lower.startswith(("what is", "what are", "what was", "what were")):
            return "factual"
        elif q_lower.startswith(("show", "list", "find", "get")):
            return "retrieval"
        elif q_lower.startswith(("compare", "difference", "versus", "vs")):
            return "comparison"
        elif any(w in q_lower for w in ["trend", "over time", "change"]):
            return "trend"
        elif any(w in q_lower for w in ["average", "mean", "median", "sum", "total"]):
            return "aggregation"
        elif any(w in q_lower for w in ["highest", "lowest", "most", "least", "top", "bottom"]):
            return "extreme"
        elif any(w in q_lower for w in ["chart", "graph", "plot", "visualize"]):
            return "visualization"
        else:
            return "general"