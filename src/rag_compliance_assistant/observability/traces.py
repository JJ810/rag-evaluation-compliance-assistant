from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rag_compliance_assistant.domain.models import GuardrailResult, RetrievedChunk


@dataclass(frozen=True)
class TraceRecord:
    id: int
    timestamp: str
    query: str
    answer: str
    model_provider: str
    embedding_provider: str
    guardrail_decision: str
    guardrail_allowed: bool
    confidence: str
    retrieved_sources: list[dict[str, Any]]
    evaluation_case_id: str | None


class TraceStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS query_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    query TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    model_provider TEXT NOT NULL,
                    embedding_provider TEXT NOT NULL,
                    guardrail_decision TEXT NOT NULL,
                    guardrail_allowed INTEGER NOT NULL,
                    confidence TEXT NOT NULL,
                    retrieved_sources_json TEXT NOT NULL,
                    evaluation_case_id TEXT
                )
                """
            )

    def record(
        self,
        *,
        query: str,
        answer: str,
        model_provider: str,
        embedding_provider: str,
        guardrail: GuardrailResult,
        confidence: str,
        retrieved_chunks: list[RetrievedChunk],
        evaluation_case_id: str | None = None,
    ) -> int:
        retrieved_sources = [
            {
                "source": result.chunk.source,
                "title": result.chunk.title,
                "chunk_id": result.chunk.id,
                "chunk_index": result.chunk.chunk_index,
                "score": round(result.score, 6),
                "overlap_terms": result.overlap_terms,
            }
            for result in retrieved_chunks
        ]
        timestamp = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO query_traces (
                    timestamp,
                    query,
                    answer,
                    model_provider,
                    embedding_provider,
                    guardrail_decision,
                    guardrail_allowed,
                    confidence,
                    retrieved_sources_json,
                    evaluation_case_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    query,
                    answer,
                    model_provider,
                    embedding_provider,
                    guardrail.decision,
                    1 if guardrail.allowed else 0,
                    confidence,
                    json.dumps(retrieved_sources, sort_keys=True),
                    evaluation_case_id,
                ),
            )
            if cursor.lastrowid is None:
                raise RuntimeError("SQLite did not return a trace row id")
            return cursor.lastrowid

    def list_recent(self, limit: int = 50) -> list[TraceRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM query_traces
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def summary(self) -> dict[str, Any]:
        with self._connect() as connection:
            total = connection.execute("SELECT COUNT(*) FROM query_traces").fetchone()[0]
            blocked = connection.execute(
                "SELECT COUNT(*) FROM query_traces WHERE guardrail_allowed = 0"
            ).fetchone()[0]
            by_provider_rows = connection.execute(
                """
                SELECT model_provider, COUNT(*) AS count
                FROM query_traces
                GROUP BY model_provider
                """
            ).fetchall()
        return {
            "total_queries": int(total),
            "guardrail_blocks": int(blocked),
            "model_provider_counts": {
                str(row["model_provider"]): int(row["count"]) for row in by_provider_rows
            },
        }

    def _row_to_record(self, row: sqlite3.Row) -> TraceRecord:
        return TraceRecord(
            id=int(row["id"]),
            timestamp=str(row["timestamp"]),
            query=str(row["query"]),
            answer=str(row["answer"]),
            model_provider=str(row["model_provider"]),
            embedding_provider=str(row["embedding_provider"]),
            guardrail_decision=str(row["guardrail_decision"]),
            guardrail_allowed=bool(row["guardrail_allowed"]),
            confidence=str(row["confidence"]),
            retrieved_sources=list(json.loads(str(row["retrieved_sources_json"]))),
            evaluation_case_id=row["evaluation_case_id"],
        )
