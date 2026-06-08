from __future__ import annotations

from functools import lru_cache

from rag_compliance_assistant.config import Settings, get_settings
from rag_compliance_assistant.eval.service import EvaluationService
from rag_compliance_assistant.guardrails.engine import GuardrailEngine
from rag_compliance_assistant.ingestion.service import IngestionService
from rag_compliance_assistant.llm.providers import build_llm_provider
from rag_compliance_assistant.observability.metrics import MetricsService
from rag_compliance_assistant.observability.traces import TraceStore
from rag_compliance_assistant.rag.embeddings import build_embedding_provider
from rag_compliance_assistant.rag.service import RagService
from rag_compliance_assistant.rag.vector_store import LocalVectorStore


@lru_cache
def get_rag_service() -> RagService:
    settings = get_settings()
    embedding_provider = build_embedding_provider(settings)
    vector_store = LocalVectorStore(settings.vector_store_path)
    ingestion_service = IngestionService(settings, embedding_provider, vector_store)
    trace_store = TraceStore(settings.trace_db_path)
    return RagService(
        settings=settings,
        embedding_provider=embedding_provider,
        llm_provider=build_llm_provider(settings),
        vector_store=vector_store,
        ingestion_service=ingestion_service,
        guardrails=GuardrailEngine(),
        trace_store=trace_store,
    )


@lru_cache
def get_evaluation_service() -> EvaluationService:
    return EvaluationService(get_settings(), get_rag_service())


@lru_cache
def get_trace_store() -> TraceStore:
    return TraceStore(get_settings().trace_db_path)


@lru_cache
def get_metrics_service() -> MetricsService:
    settings: Settings = get_settings()
    return MetricsService(settings, get_trace_store())
