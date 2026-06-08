from __future__ import annotations

from rag_compliance_assistant.rag.service import RagService
from rag_compliance_assistant.rag.text import tokenize


def test_mock_answer_is_concise_and_readable(rag_service: RagService) -> None:
    rag_service.ingest()

    result = rag_service.ask(
        "Can employees paste confidential customer data into unapproved public AI tools?",
        top_k=5,
    )

    assert result.answer.startswith("No.")
    assert "Employees must not paste confidential customer data" in result.answer
    assert "[ai_usage_policy.md#chunk-" in result.answer
    assert "#" not in result.answer.replace("[ai_usage_policy.md#chunk-", "")
    assert "synthetic policy" not in result.answer.lower()
    assert len(tokenize(result.answer)) <= 60


def test_query_response_filters_weak_evidence_chunks(rag_service: RagService) -> None:
    rag_service.ingest()

    result = rag_service.ask(
        "Can employees paste confidential customer data into unapproved public AI tools?",
        top_k=5,
    )

    assert result.retrieved_chunks
    assert {chunk.chunk.source for chunk in result.retrieved_chunks} == {"ai_usage_policy.md"}
    assert {citation.source for citation in result.citations} == {"ai_usage_policy.md"}
