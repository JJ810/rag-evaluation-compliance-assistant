# ADR 0001: V1 Local-First RAG Architecture

## Status

Accepted

## Context

The project is a public portfolio flagship. It must be impressive, reproducible, safe for public review, and runnable without paid services.

## Decision

V1 uses:

- FastAPI backend;
- Streamlit UI;
- Markdown/TXT synthetic policy corpus;
- deterministic chunking;
- mock feature-hashing embeddings by default;
- optional OpenAI providers through environment variables;
- JSON-backed local vector store;
- SQLite trace store;
- pytest, ruff, mypy, Docker, and GitHub Actions.

## Consequences

Benefits:

- no cloud credentials required;
- tests are deterministic;
- generated artifacts are inspectable;
- architecture remains easy to explain;
- OpenAI support is available without making it mandatory.

Tradeoffs:

- local vector store is not meant for scale;
- mock embeddings are not semantic embeddings;
- PDF support is deferred;
- guardrails are intentionally simple.

Future architecture changes should add or update ADRs.
