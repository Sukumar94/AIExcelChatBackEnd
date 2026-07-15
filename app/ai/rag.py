"""
RAG (Retrieval-Augmented Generation) service.
Uses FAISS for vector similarity search on workbook schemas and previous queries.
"""

from __future__ import annotations

import json
import logging
import os
import pickle
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.ai.embeddings import EmbeddingService
from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """
    Retrieval-Augmented Generation service.
    Stores and retrieves relevant context for LLM queries.
    """

    def __init__(self) -> None:
        self.embedder = EmbeddingService()
        self.dimension = 768
        self.index_path = Path(settings.faiss_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.index: faiss.IndexFlatL2 | None = None
        self.documents: list[dict[str, Any]] = []
        self._load_index()

    def _load_index(self) -> None:
        """Load existing FAISS index if available."""
        index_file = self.index_path / "faiss.index"
        docs_file = self.index_path / "documents.pkl"
        if index_file.exists() and docs_file.exists():
            try:
                self.index = faiss.read_index(str(index_file))
                with open(docs_file, "rb") as f:
                    self.documents = pickle.load(f)
                logger.info("Loaded FAISS index with %d documents", len(self.documents))
            except Exception as e:
                logger.warning("Failed to load FAISS index: %s", e)
                self._create_index()

    def _create_index(self) -> None:
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        logger.info("Created new FAISS index")

    def _save_index(self) -> None:
        """Save the FAISS index to disk."""
        if self.index is None:
            return
        try:
            faiss.write_index(self.index, str(self.index_path / "faiss.index"))
            with open(self.index_path / "documents.pkl", "wb") as f:
                pickle.dump(self.documents, f)
        except Exception as e:
            logger.warning("Failed to save FAISS index: %s", e)

    def add_document(self, text: str, metadata: dict[str, Any] | None = None) -> None:
        """Add a document to the index."""
        if self.index is None:
            self._create_index()

        embedding = self.embedder.embed(text)
        self.index.add(np.array([embedding], dtype=np.float32))  # type: ignore
        self.documents.append({
            "text": text,
            "metadata": metadata or {},
        })
        self._save_index()

    def add_workbook_context(self, session_id: str, sheet_name: str, schema_text: str) -> None:
        """Add workbook schema context for retrieval."""
        self.add_document(
            text=schema_text,
            metadata={"type": "schema", "session_id": session_id, "sheet_name": sheet_name},
        )

    def add_query_history(self, session_id: str, question: str, answer: str, sql: str | None = None) -> None:
        """Add a previous Q&A pair for context."""
        text = f"Q: {question}\nA: {answer}"
        if sql:
            text += f"\nSQL: {sql}"
        self.add_document(
            text=text,
            metadata={"type": "qa", "session_id": session_id, "question": question},
        )

    def retrieve(self, query: str, k: int = 3) -> list[dict[str, Any]]:
        """Retrieve the top-k most relevant documents."""
        if self.index is None or self.index.ntotal == 0:
            return []

        query_embedding = self.embedder.embed(query)
        distances, indices = self.index.search(
            np.array([query_embedding], dtype=np.float32), k
        )

        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.documents):
                results.append({
                    **self.documents[idx],
                    "score": float(distances[0][i]),
                })
        return results

    def get_relevant_context(self, query: str, session_id: str | None = None, k: int = 3) -> str:
        """Get relevant context as a formatted string for LLM prompts."""
        results = self.retrieve(query, k=k)
        if not results:
            return ""

        # Filter by session if provided
        if session_id:
            results = [r for r in results if r.get("metadata", {}).get("session_id") == session_id]

        context_parts = []
        for r in results:
            context_parts.append(r["text"])

        return "\n\n---\n\n".join(context_parts)