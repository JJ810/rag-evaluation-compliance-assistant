from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rag_compliance_assistant.config import Settings
from rag_compliance_assistant.ingestion.chunking import chunk_documents
from rag_compliance_assistant.ingestion.loaders import load_documents
from rag_compliance_assistant.rag.embeddings import EmbeddingProvider
from rag_compliance_assistant.rag.vector_store import LocalVectorStore


@dataclass(frozen=True)
class IngestionReport:
    documents_loaded: int
    chunks_indexed: int
    vector_store_path: str


class IngestionService:
    def __init__(
        self,
        settings: Settings,
        embedding_provider: EmbeddingProvider,
        vector_store: LocalVectorStore,
    ) -> None:
        self._settings = settings
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def ingest_directory(self, directory: Path | None = None) -> IngestionReport:
        docs_dir = directory or self._settings.sample_docs_dir
        documents = load_documents(docs_dir)
        chunks = chunk_documents(
            documents,
            chunk_size_words=self._settings.chunk_size_words,
            overlap_words=self._settings.chunk_overlap_words,
        )
        embeddings = self._embedding_provider.embed_texts([chunk.text for chunk in chunks])
        self._vector_store.index(chunks, embeddings)
        return IngestionReport(
            documents_loaded=len(documents),
            chunks_indexed=len(chunks),
            vector_store_path=str(self._settings.vector_store_path),
        )
