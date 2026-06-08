from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any

from rag_compliance_assistant.domain.models import Chunk, RetrievedChunk
from rag_compliance_assistant.rag.text import count_overlap


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


class LocalVectorStore:
    """Tiny local vector store persisted as JSON for reproducible V1 demos."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._items: list[dict[str, Any]] = []
        self.load()

    @property
    def count(self) -> int:
        return len(self._items)

    def is_ready(self) -> bool:
        return self.count > 0

    def load(self) -> None:
        if not self.path.exists():
            self._items = []
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self._items = list(payload.get("items", []))

    def index(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        self._items = [
            {
                "chunk": asdict(chunk),
                "embedding": embedding,
            }
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ]
        self.persist()

    def persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"schema_version": 1, "items": self._items}
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def search(self, query: str, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        scored: list[RetrievedChunk] = []
        for item in self._items:
            chunk_payload = item["chunk"]
            chunk = Chunk(
                id=chunk_payload["id"],
                document_id=chunk_payload["document_id"],
                source=chunk_payload["source"],
                title=chunk_payload["title"],
                text=chunk_payload["text"],
                chunk_index=int(chunk_payload["chunk_index"]),
                metadata=dict(chunk_payload.get("metadata", {})),
            )
            score = cosine_similarity(query_embedding, list(item["embedding"]))
            overlap_terms = count_overlap(query, chunk.text)
            scored.append(RetrievedChunk(chunk=chunk, score=score, overlap_terms=overlap_terms))

        scored.sort(key=lambda result: (result.score, result.overlap_terms), reverse=True)
        return scored[:top_k]
