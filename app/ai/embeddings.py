"""
Embeddings service - generates vector embeddings using Ollama.
Includes fallback for when Ollama is unavailable.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import ollama

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generates text embeddings using Ollama's embedding models.
    Uses nomic-embed-text by default (768 dimensions).
    Falls back to zero embeddings if service unavailable.
    """

    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.embedding_model
        self.dimension = 768  # nomic-embed-text
        self.available = self._check_available()
        try:
            ollama._client._base_url = settings.ollama_url
        except Exception as e:
            logger.warning("Failed to configure Ollama client for embeddings: %s", e)
            self.available = False

    def _check_available(self) -> bool:
        """Check if Ollama embedding service is available."""
        try:
            import httpx
            client = httpx.Client(timeout=1.0)  # Reduced from 2.0 for faster fallback
            response = client.get(f"{settings.ollama_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text string."""
        if not self.available:
            # Return dummy embedding to allow RAG to continue working
            logger.debug("Using fallback embedding (Ollama unavailable)")
            return [0.0] * self.dimension
        
        try:
            response = ollama.embeddings(model=self.model, prompt=text)
            return response["embedding"]
        except Exception as e:
            logger.warning("Embedding failed: %s - using fallback", e)
            self.available = False
            return [0.0] * self.dimension

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        return [self.embed(t) for t in texts]

    def embed_dataframe_context(self, df_summary: str) -> list[float]:
        """Generate embedding for a DataFrame summary (for RAG retrieval)."""
        return self.embed(df_summary)