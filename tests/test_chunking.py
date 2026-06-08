from __future__ import annotations

from rag_compliance_assistant.domain.models import Document
from rag_compliance_assistant.ingestion.chunking import chunk_document


def test_chunking_is_deterministic_and_overlapping() -> None:
    text = " ".join(f"word{i}" for i in range(25))
    document = Document(id="doc_test", source="sample.md", title="Sample", text=text)

    chunks = chunk_document(document, chunk_size_words=10, overlap_words=2)
    repeated = chunk_document(document, chunk_size_words=10, overlap_words=2)

    assert [chunk.id for chunk in chunks] == [chunk.id for chunk in repeated]
    assert len(chunks) == 3
    assert chunks[0].text.split()[-2:] == chunks[1].text.split()[:2]
    assert chunks[1].chunk_index == 1
