from __future__ import annotations

from rag_compliance_assistant.config import Settings
from rag_compliance_assistant.domain.models import (
    AnswerResult,
    Citation,
    Confidence,
    GuardrailResult,
    RetrievedChunk,
)
from rag_compliance_assistant.guardrails.engine import GuardrailEngine
from rag_compliance_assistant.ingestion.service import IngestionService
from rag_compliance_assistant.llm.providers import LLMProvider
from rag_compliance_assistant.observability.traces import TraceStore
from rag_compliance_assistant.rag.embeddings import EmbeddingProvider
from rag_compliance_assistant.rag.evidence import select_supporting_sentence
from rag_compliance_assistant.rag.vector_store import LocalVectorStore

INSUFFICIENT_EVIDENCE = "I do not have enough evidence in the retrieved documents to answer that."


class RagService:
    def __init__(
        self,
        *,
        settings: Settings,
        embedding_provider: EmbeddingProvider,
        llm_provider: LLMProvider,
        vector_store: LocalVectorStore,
        ingestion_service: IngestionService,
        guardrails: GuardrailEngine,
        trace_store: TraceStore,
    ) -> None:
        self._settings = settings
        self._embedding_provider = embedding_provider
        self._llm_provider = llm_provider
        self._vector_store = vector_store
        self._ingestion_service = ingestion_service
        self._guardrails = guardrails
        self._trace_store = trace_store

    def ingest(self) -> dict[str, int | str]:
        report = self._ingestion_service.ingest_directory()
        return {
            "documents_loaded": report.documents_loaded,
            "chunks_indexed": report.chunks_indexed,
            "vector_store_path": report.vector_store_path,
        }

    def ask(
        self,
        query: str,
        *,
        top_k: int | None = None,
        evaluation_case_id: str | None = None,
    ) -> AnswerResult:
        query_guardrail = self._guardrails.check_query(query)
        if not query_guardrail.allowed:
            answer = INSUFFICIENT_EVIDENCE
            trace_id = self._trace_store.record(
                query=query,
                answer=answer,
                model_provider=self._llm_provider.name,
                embedding_provider=self._embedding_provider.name,
                guardrail=query_guardrail,
                confidence="low",
                retrieved_chunks=[],
                evaluation_case_id=evaluation_case_id,
            )
            return AnswerResult(
                answer=answer,
                citations=[],
                confidence="low",
                retrieved_chunks=[],
                guardrail=query_guardrail,
                model_provider=self._llm_provider.name,
                embedding_provider=self._embedding_provider.name,
                trace_id=trace_id,
            )

        self._ensure_index_ready()
        resolved_top_k = top_k or self._settings.retrieval_top_k
        query_embedding = self._embedding_provider.embed_texts([query])[0]
        retrieved_chunks = self._vector_store.search(query, query_embedding, resolved_top_k)
        evidence_chunks = self._filter_relevant_chunks(retrieved_chunks)

        if not self._has_sufficient_evidence(evidence_chunks):
            answer = INSUFFICIENT_EVIDENCE
            guardrail = GuardrailResult(
                allowed=True,
                decision="insufficient_context",
                reasons=["Retrieved context did not pass the relevance threshold."],
            )
            trace_id = self._trace_store.record(
                query=query,
                answer=answer,
                model_provider=self._llm_provider.name,
                embedding_provider=self._embedding_provider.name,
                guardrail=guardrail,
                confidence="low",
                retrieved_chunks=evidence_chunks,
                evaluation_case_id=evaluation_case_id,
            )
            return AnswerResult(
                answer=answer,
                citations=[],
                confidence="low",
                retrieved_chunks=evidence_chunks,
                guardrail=guardrail,
                model_provider=self._llm_provider.name,
                embedding_provider=self._embedding_provider.name,
                trace_id=trace_id,
            )

        generated = self._llm_provider.generate(query, evidence_chunks)
        citations = self._build_citations(query, evidence_chunks)
        confidence = self._classify_confidence(evidence_chunks)
        answer_guardrail = self._guardrails.check_answer(
            generated.text,
            citations,
            required=True,
        )
        answer = generated.text
        if not answer_guardrail.allowed:
            answer = (
                "The system found potentially relevant context, but the generated answer failed "
                "citation guardrails. Inspect the retrieved chunks before using this answer."
            )
            confidence = "low"

        trace_id = self._trace_store.record(
            query=query,
            answer=answer,
            model_provider=generated.provider,
            embedding_provider=self._embedding_provider.name,
            guardrail=answer_guardrail,
            confidence=confidence,
            retrieved_chunks=evidence_chunks,
            evaluation_case_id=evaluation_case_id,
        )
        return AnswerResult(
            answer=answer,
            citations=citations,
            confidence=confidence,
            retrieved_chunks=evidence_chunks,
            guardrail=answer_guardrail,
            model_provider=generated.provider,
            embedding_provider=self._embedding_provider.name,
            trace_id=trace_id,
        )

    def _ensure_index_ready(self) -> None:
        if not self._vector_store.is_ready():
            self._ingestion_service.ingest_directory()

    def _has_sufficient_evidence(self, retrieved_chunks: list[RetrievedChunk]) -> bool:
        if not retrieved_chunks:
            return False
        top = retrieved_chunks[0]
        return (
            top.score >= self._settings.retrieval_min_score
            and top.overlap_terms >= self._settings.retrieval_min_overlap_terms
        )

    def _filter_relevant_chunks(
        self, retrieved_chunks: list[RetrievedChunk]
    ) -> list[RetrievedChunk]:
        if not retrieved_chunks:
            return []
        top = retrieved_chunks[0]
        if not self._has_sufficient_evidence([top]):
            return []

        score_floor = max(self._settings.retrieval_min_score, top.score * 0.75)
        filtered = [
            result
            for result in retrieved_chunks
            if result.score >= score_floor
            and result.overlap_terms >= self._settings.retrieval_min_overlap_terms
        ]
        return filtered or [top]

    def _classify_confidence(self, retrieved_chunks: list[RetrievedChunk]) -> Confidence:
        top_score = retrieved_chunks[0].score if retrieved_chunks else 0.0
        distinct_sources = {result.chunk.source for result in retrieved_chunks[:3]}
        if top_score >= 0.55 and len(distinct_sources) >= 1:
            return "high"
        if top_score >= 0.32:
            return "medium"
        return "low"

    def _build_citations(
        self,
        query: str,
        retrieved_chunks: list[RetrievedChunk],
    ) -> list[Citation]:
        citations: list[Citation] = []
        for result in retrieved_chunks[:3]:
            quote = select_supporting_sentence(query, result.chunk.text)
            if quote is None:
                quote = result.chunk.text[:280].strip()
                if len(result.chunk.text) > 280:
                    quote = f"{quote}..."
            citations.append(
                Citation(
                    source=result.chunk.source,
                    title=result.chunk.title,
                    chunk_id=result.chunk.id,
                    quote=quote,
                )
            )
        return citations
