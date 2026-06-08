# Limitations

V1 is intentionally medium complexity: strong enough to demonstrate engineering maturity, small enough to understand and maintain.

## Current Limits

- Markdown and TXT ingestion only.
- JSON-backed local vector store, not a high-scale vector database.
- Mock embeddings are deterministic approximations, not semantic embeddings.
- Mock LLM provider extracts context sentences; it does not perform deep reasoning.
- OpenAI provider is optional and not used by tests.
- Groundedness is measured with a lexical heuristic.
- Guardrails are regex-based and incomplete.
- No authentication or authorization.
- No hosted deployment configuration beyond Docker.
- No real confidential data, real PII, or production compliance documents.

## Why These Limits Are Acceptable For V1

The goal is to show professional AI engineering patterns: provider abstraction, retrieval, citations, evaluation, safety checks, traces, reproducibility, tests, and documentation. The system is not claiming to be a finished enterprise compliance platform.

## Future Improvements

- PDF parser with secure file handling.
- ChromaDB, pgvector, or OpenSearch adapter.
- Dataset versioning and richer eval coverage.
- Model-graded eval with budget controls.
- Authentication, authorization, and tenant isolation.
- Real observability backend.
- Human feedback loop.
- ADRs for architecture changes.
