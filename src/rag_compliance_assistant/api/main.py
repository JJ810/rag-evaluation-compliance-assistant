from __future__ import annotations

from dataclasses import asdict

from fastapi import Depends, FastAPI

from rag_compliance_assistant.api.dependencies import (
    get_evaluation_service,
    get_metrics_service,
    get_rag_service,
    get_trace_store,
)
from rag_compliance_assistant.api.schemas import (
    EvaluationRequest,
    EvaluationResponse,
    HealthResponse,
    IngestResponse,
    MetricsResponse,
    QueryRequest,
    QueryResponse,
    TraceResponse,
)
from rag_compliance_assistant.config import Settings, get_settings
from rag_compliance_assistant.domain.models import AnswerResult
from rag_compliance_assistant.eval.service import EvaluationService
from rag_compliance_assistant.observability.metrics import MetricsService
from rag_compliance_assistant.observability.traces import TraceStore
from rag_compliance_assistant.rag.service import RagService

app = FastAPI(
    title="Enterprise RAG Evaluation & Compliance Assistant",
    version="0.1.0",
    description="Local-first RAG API with evaluation, guardrails, citations, metrics, and traces.",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        providers={
            "llm": settings.llm_provider,
            "embedding": settings.embedding_provider,
        },
    )


@app.post("/ingest", response_model=IngestResponse, tags=["rag"])
def ingest(rag_service: RagService = Depends(get_rag_service)) -> IngestResponse:
    return IngestResponse(**rag_service.ingest())


@app.post("/query", response_model=QueryResponse, tags=["rag"])
def query(
    request: QueryRequest,
    rag_service: RagService = Depends(get_rag_service),
) -> QueryResponse:
    return _answer_to_response(rag_service.ask(request.query, top_k=request.top_k))


@app.post("/evaluate", response_model=EvaluationResponse, tags=["evaluation"])
def evaluate(
    request: EvaluationRequest,
    evaluation_service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationResponse:
    report = evaluation_service.run(top_k=request.top_k)
    return EvaluationResponse(report=report)


@app.get("/metrics", response_model=MetricsResponse, tags=["observability"])
def metrics(metrics_service: MetricsService = Depends(get_metrics_service)) -> MetricsResponse:
    return MetricsResponse(metrics=metrics_service.snapshot())


@app.get("/traces", response_model=TraceResponse, tags=["observability"])
def traces(
    limit: int = 50,
    trace_store: TraceStore = Depends(get_trace_store),
) -> TraceResponse:
    limit = max(1, min(limit, 200))
    return TraceResponse(traces=[asdict(record) for record in trace_store.list_recent(limit)])


def _answer_to_response(result: AnswerResult) -> QueryResponse:
    return QueryResponse(
        answer=result.answer,
        confidence=result.confidence,
        citations=[asdict(citation) for citation in result.citations],
        retrieved_chunks=[
            {
                "source": retrieved.chunk.source,
                "title": retrieved.chunk.title,
                "chunk_id": retrieved.chunk.id,
                "chunk_index": retrieved.chunk.chunk_index,
                "score": retrieved.score,
                "overlap_terms": retrieved.overlap_terms,
                "text": retrieved.chunk.text,
                "metadata": retrieved.chunk.metadata,
            }
            for retrieved in result.retrieved_chunks
        ],
        guardrail=asdict(result.guardrail),
        providers={
            "llm": result.model_provider,
            "embedding": result.embedding_provider,
        },
        trace_id=result.trace_id,
    )


def create_app() -> FastAPI:
    return app
