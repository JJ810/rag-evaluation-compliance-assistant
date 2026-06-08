from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Confidence = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class Document:
    id: str
    source: str
    title: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    source: str
    title: str
    text: str
    chunk_index: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    score: float
    overlap_terms: int = 0


@dataclass(frozen=True)
class Citation:
    source: str
    title: str
    chunk_id: str
    quote: str


@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    decision: str
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AnswerResult:
    answer: str
    citations: list[Citation]
    confidence: Confidence
    retrieved_chunks: list[RetrievedChunk]
    guardrail: GuardrailResult
    model_provider: str
    embedding_provider: str
    trace_id: int | None = None
