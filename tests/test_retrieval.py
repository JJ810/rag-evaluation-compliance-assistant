from __future__ import annotations

from rag_compliance_assistant.rag.service import RagService


def test_retrieval_returns_expected_policy_source(rag_service: RagService) -> None:
    rag_service.ingest()

    result = rag_service.ask("How long are customer support tickets retained after closure?")

    assert result.retrieved_chunks
    assert result.retrieved_chunks[0].chunk.source == "data_retention_policy.md"
    assert result.confidence in {"medium", "high"}
    assert "data_retention_policy.md#chunk-" in result.answer
