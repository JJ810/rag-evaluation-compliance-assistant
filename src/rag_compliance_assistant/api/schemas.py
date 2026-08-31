from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    providers: dict[str, str]


class IngestResponse(BaseModel):
    documents_loaded: int
    chunks_indexed: int
    vector_store_path: str


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class CitationResponse(BaseModel):
    source: str
    title: str
    chunk_id: str
    quote: str


class RetrievedChunkResponse(BaseModel):
    source: str
    title: str
    chunk_id: str
    chunk_index: int
    score: float
    overlap_terms: int
    text: str
    metadata: dict[str, Any]


class GuardrailResponse(BaseModel):
    allowed: bool
    decision: str
    reasons: list[str]


class QueryResponse(BaseModel):
    answer: str
    confidence: str
    citations: list[CitationResponse]
    retrieved_chunks: list[RetrievedChunkResponse]
    guardrail: GuardrailResponse
    providers: dict[str, str]
    trace_id: int | None


class EvaluationRequest(BaseModel):
    top_k: int | None = Field(default=None, ge=1, le=20)


class EvaluationResponse(BaseModel):
    report: dict[str, Any]


class MetricsResponse(BaseModel):
    metrics: dict[str, Any]


class TraceResponse(BaseModel):
    traces: list[dict[str, Any]]
