from __future__ import annotations

from pathlib import Path

import pytest

from rag_compliance_assistant.config import Settings
from rag_compliance_assistant.guardrails.engine import GuardrailEngine
from rag_compliance_assistant.ingestion.service import IngestionService
from rag_compliance_assistant.llm.providers import MockLLMProvider
from rag_compliance_assistant.observability.traces import TraceStore
from rag_compliance_assistant.rag.embeddings import MockEmbeddingProvider
from rag_compliance_assistant.rag.service import RagService
from rag_compliance_assistant.rag.vector_store import LocalVectorStore


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_docs_dir(repo_root: Path) -> Path:
    return repo_root / "data" / "sample_docs"


@pytest.fixture
def eval_sets_dir(repo_root: Path) -> Path:
    return repo_root / "data" / "eval_sets"


@pytest.fixture
def test_settings(tmp_path: Path, sample_docs_dir: Path, eval_sets_dir: Path) -> Settings:
    settings = Settings(
        data_dir=tmp_path / "data",
        sample_docs_dir=sample_docs_dir,
        eval_sets_dir=eval_sets_dir,
        vector_store_path=tmp_path / "data" / "vector_store" / "index.json",
        trace_db_path=tmp_path / "data" / "traces" / "traces.db",
        eval_report_path=tmp_path / "reports" / "eval" / "evaluation_report.json",
        embedding_provider="mock",
        llm_provider="mock",
        chunk_size_words=80,
        chunk_overlap_words=15,
        retrieval_min_score=0.12,
    )
    settings.ensure_runtime_dirs()
    return settings


@pytest.fixture
def rag_service(test_settings: Settings) -> RagService:
    embedding_provider = MockEmbeddingProvider(test_settings.mock_embedding_dimensions)
    vector_store = LocalVectorStore(test_settings.vector_store_path)
    ingestion_service = IngestionService(test_settings, embedding_provider, vector_store)
    return RagService(
        settings=test_settings,
        embedding_provider=embedding_provider,
        llm_provider=MockLLMProvider(),
        vector_store=vector_store,
        ingestion_service=ingestion_service,
        guardrails=GuardrailEngine(),
        trace_store=TraceStore(test_settings.trace_db_path),
    )
