from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and .env files."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Enterprise RAG Evaluation & Compliance Assistant"
    app_version: str = "0.1.0"
    environment: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    data_dir: Path = Path("data")
    sample_docs_dir: Path = Path("data/sample_docs")
    eval_sets_dir: Path = Path("data/eval_sets")
    vector_store_path: Path = Path("data/vector_store/index.json")
    trace_db_path: Path = Path("data/traces/traces.db")
    eval_report_path: Path = Path("reports/eval/evaluation_report.json")

    embedding_provider: str = "mock"
    llm_provider: str = "mock"
    mock_embedding_dimensions: int = Field(default=96, ge=16, le=4096)
    openai_api_key: SecretStr | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4.1-mini"

    chunk_size_words: int = Field(default=160, ge=30, le=1000)
    chunk_overlap_words: int = Field(default=35, ge=0, le=300)
    retrieval_top_k: int = Field(default=4, ge=1, le=20)
    retrieval_min_score: float = Field(default=0.18, ge=0.0, le=1.0)
    retrieval_min_overlap_terms: int = Field(default=1, ge=0, le=20)

    def ensure_runtime_dirs(self) -> None:
        """Create runtime directories that hold generated local artifacts."""

        for path in (
            self.data_dir,
            self.sample_docs_dir,
            self.eval_sets_dir,
            self.vector_store_path.parent,
            self.trace_db_path.parent,
            self.eval_report_path.parent,
        ):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_runtime_dirs()
    return settings
