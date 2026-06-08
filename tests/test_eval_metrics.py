from __future__ import annotations

from rag_compliance_assistant.domain.models import (
    AnswerResult,
    Chunk,
    Citation,
    GuardrailResult,
    RetrievedChunk,
)
from rag_compliance_assistant.eval.metrics import (
    EvaluationCase,
    aggregate_case_metrics,
    evaluate_answer,
)


def test_evaluation_metrics_detect_source_citation_and_refusal() -> None:
    chunk = Chunk(
        id="chk_1",
        document_id="doc_1",
        source="access_control_policy.md",
        title="Access Control Policy",
        text="Employees must use multi-factor authentication for remote access.",
        chunk_index=0,
    )
    result = AnswerResult(
        answer=(
            "Employees must use multi-factor authentication for remote access. "
            "[access_control_policy.md#chunk-0]"
        ),
        citations=[
            Citation(
                source="access_control_policy.md",
                title="Access Control Policy",
                chunk_id="chk_1",
                quote=chunk.text,
            )
        ],
        confidence="high",
        retrieved_chunks=[RetrievedChunk(chunk=chunk, score=0.9, overlap_terms=3)],
        guardrail=GuardrailResult(allowed=True, decision="answer_allowed"),
        model_provider="mock",
        embedding_provider="mock",
    )
    case = EvaluationCase(
        id="case_1",
        query="What is required for remote access?",
        expected_sources=["access_control_policy.md"],
    )

    case_result = evaluate_answer(case, result)
    aggregate = aggregate_case_metrics([case_result])

    assert case_result["hit_at_k"] is True
    assert case_result["citation_present"] is True
    assert aggregate["retrieval_hit_rate"] == 1.0
    assert aggregate["citation_presence_rate"] == 1.0
