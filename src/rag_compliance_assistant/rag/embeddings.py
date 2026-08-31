from __future__ import annotations

import hashlib
import math
from typing import Protocol

from rag_compliance_assistant.config import Settings
from rag_compliance_assistant.rag.text import tokenize


class EmbeddingProvider(Protocol):
    name: str

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts."""


class MockEmbeddingProvider:
    """Deterministic no-cost embedding provider based on feature hashing."""

    name = "mock"

    def __init__(self, dimensions: int = 96) -> None:
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text, remove_stopwords=True):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class OpenAIEmbeddingProvider:
    """OpenAI embedding provider used only when explicitly configured."""

    name = "openai"

    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(
            model=self._model,
            input=texts,
            encoding_format="float",
        )
        return [list(item.embedding) for item in response.data]


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    provider = settings.embedding_provider.lower()
    if provider == "mock":
        return MockEmbeddingProvider(dimensions=settings.mock_embedding_dimensions)
    if provider == "openai":
        if settings.openai_api_key is None:
            raise ValueError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai")
        api_key = settings.openai_api_key.get_secret_value().strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY must not be empty when EMBEDDING_PROVIDER=openai")
        return OpenAIEmbeddingProvider(
            api_key=api_key,
            model=settings.openai_embedding_model,
        )
    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
