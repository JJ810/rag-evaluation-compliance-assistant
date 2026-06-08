from __future__ import annotations

import hashlib
import re

from rag_compliance_assistant.domain.models import Chunk, Document

_WHITESPACE_RE = re.compile(r"\s+")


def _stable_chunk_id(document_id: str, chunk_index: int, text: str) -> str:
    digest = hashlib.sha1(f"{document_id}:{chunk_index}:{text}".encode()).hexdigest()
    return f"chk_{digest[:16]}"


def normalize_text(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text).strip()


def chunk_document(document: Document, chunk_size_words: int, overlap_words: int) -> list[Chunk]:
    """Split one document into deterministic overlapping word chunks."""

    if chunk_size_words <= 0:
        raise ValueError("chunk_size_words must be positive")
    if overlap_words >= chunk_size_words:
        raise ValueError("overlap_words must be smaller than chunk_size_words")

    words = normalize_text(document.text).split()
    if not words:
        return []

    chunks: list[Chunk] = []
    start = 0
    index = 0
    step = chunk_size_words - overlap_words
    while start < len(words):
        window = words[start : start + chunk_size_words]
        chunk_text = " ".join(window)
        chunks.append(
            Chunk(
                id=_stable_chunk_id(document.id, index, chunk_text),
                document_id=document.id,
                source=document.source,
                title=document.title,
                text=chunk_text,
                chunk_index=index,
                metadata={**document.metadata, "chunk_size_words": len(window)},
            )
        )
        if start + chunk_size_words >= len(words):
            break
        start += step
        index += 1
    return chunks


def chunk_documents(
    documents: list[Document], chunk_size_words: int, overlap_words: int
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        chunks.extend(chunk_document(document, chunk_size_words, overlap_words))
    return chunks
