# Enterprise RAG Evaluation & Compliance Assistant

Local-first, production-style GenAI/RAG portfolio project for demonstrating applied AI engineering, LLM engineering, evaluation, guardrails, observability, API design, security practices, cost control, CI/CD, and bilingual documentation.

This project is intentionally **not** a generic chatbot. It is a compliance-oriented RAG system that retrieves local policy evidence, generates cited answers, refuses unsupported questions, records traces, and evaluates retrieval and answer behavior with deterministic mock providers.

## What This Demonstrates

- FastAPI backend with health, ingestion, query, evaluation, metrics, and trace endpoints.
- Deterministic RAG pipeline with local sample documents, chunking, embeddings, vector search, citations, confidence labels, and source metadata.
- Pluggable providers: no-cost mock embeddings and mock LLM by default, optional OpenAI embeddings and chat model when `OPENAI_API_KEY` is configured.
- Evaluation system for hit@k, source match accuracy, citation presence, groundedness heuristic, refusal behavior, and answer length sanity.
- Deterministic guardrails for prompt injection attempts, secret requests, missing citations, unsupported questions, and out-of-scope requests.
- Local SQLite query traces and metrics endpoint.
- Minimal Streamlit UI for asking questions, inspecting citations and retrieved chunks, and running evaluation.
- Pytest, ruff, mypy, pytest-cov, pre-commit, Docker, GitHub Actions, CodeQL, Dependabot, and Release Please configuration.
- Security and cost-control documentation suitable for a public portfolio repository.

## Architecture

```text
Sample docs -> Loader -> Deterministic chunks -> Embedding provider
                                           -> Local vector store

User query -> Guardrails -> Query embedding -> Retrieval -> LLM provider
                                                   -> citations/confidence
                                                   -> SQLite trace
                                                   -> API/UI response

Evaluation set -> RAG service -> retrieval metrics + answer heuristics -> JSON report
```

Core package: `src/rag_compliance_assistant`

- `api/`: FastAPI app, schemas, dependency wiring.
- `ingestion/`: Markdown/TXT loading and deterministic chunking.
- `rag/`: embeddings, vector store, retrieval orchestration.
- `llm/`: mock and OpenAI LLM providers.
- `guardrails/`: deterministic safety checks.
- `eval/`: synthetic evaluation logic and aggregate metrics.
- `observability/`: SQLite traces and metrics snapshots.
- `ui/`: Streamlit interface.

See [docs/architecture.md](docs/architecture.md) for more detail.

## How Mock-Mode RAG Works Without API Keys

The default `mock/mock` configuration is a real local RAG flow with deterministic providers:

1. local Markdown/TXT policy documents are loaded from `data/sample_docs`;
2. documents are split into stable overlapping chunks;
3. `MockEmbeddingProvider` creates deterministic feature-hashing embeddings with no network calls;
4. the local JSON vector store ranks chunks with cosine similarity;
5. low-relevance chunks are filtered before citations and UI display;
6. `MockLLMProvider` selects the strongest supporting policy sentence and formats a concise cited answer;
7. guardrails verify citations, refusals, and obvious unsafe requests;
8. traces are written locally to SQLite.

This means tests, CI, local demos, and Docker smoke checks do not require `OPENAI_API_KEY` and do not incur provider cost. Optional OpenAI mode only swaps the embedding and LLM providers after you explicitly configure environment variables.

## Local Setup

Python 3.11+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The default configuration uses mock providers and does not require cloud credentials.

Optional OpenAI mode:

```bash
cp .env.example .env
# edit .env, set OPENAI_API_KEY, EMBEDDING_PROVIDER=openai, LLM_PROVIDER=openai
```

Never commit `.env` or real secrets.

## Commands

GNU Make targets are provided for macOS/Linux and Windows environments that have `make` installed:

```bash
make ingest      # index sample policy documents
make eval        # run synthetic evaluation and write reports/eval/evaluation_report.json
make api         # start FastAPI at http://localhost:8000
make ui          # start Streamlit UI
make lint        # ruff lint + format check
make type        # mypy
make test        # pytest with coverage
make docker-up   # local API + UI through Docker Compose
```

Windows PowerShell direct commands:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts\ingest.py
python scripts\run_eval.py
python -m uvicorn rag_compliance_assistant.api.main:app --host 127.0.0.1 --port 8000 --reload
python -m streamlit run src\rag_compliance_assistant\ui\app.py
```

macOS/Linux direct commands:

```bash
python scripts/ingest.py
python scripts/run_eval.py
python -m uvicorn rag_compliance_assistant.api.main:app --reload
python -m streamlit run src/rag_compliance_assistant/ui/app.py
```

## API Usage

Health:

```powershell
curl.exe http://127.0.0.1:8000/health
```

Ingest sample documents:

```powershell
curl.exe -X POST http://127.0.0.1:8000/ingest
```

Ask a compliance question:

```powershell
curl.exe -X POST http://127.0.0.1:8000/query `
  -H "Content-Type: application/json" `
  -d '{"query":"Can employees paste confidential customer data into unapproved public AI tools?","top_k":4}'
```

Run evaluation:

```powershell
curl.exe -X POST http://127.0.0.1:8000/evaluate `
  -H "Content-Type: application/json" `
  -d '{"top_k":4}'
```

Inspect traces and metrics:

```powershell
curl.exe http://127.0.0.1:8000/traces
curl.exe http://127.0.0.1:8000/metrics
```

## Evaluation

The evaluation dataset lives in `data/eval_sets/synthetic_compliance_eval.json`.

The report includes:

- retrieval hit rate;
- mean source match accuracy;
- citation presence rate;
- groundedness heuristic;
- refusal accuracy;
- answer length sanity rate;
- case-level retrieved sources and guardrail decisions.

Run:

```bash
python scripts/run_eval.py
```

Details: [docs/evaluation.md](docs/evaluation.md).

## Guardrails

The project includes simple, deterministic, testable guardrails for:

- prompt injection attempts;
- requests to reveal secrets or credentials;
- unsupported/out-of-scope queries;
- missing citation markers in generated answers;
- insufficient retrieved context.

These guardrails are intentionally modest. They are useful for portfolio demonstration and regression tests, but they are not complete security controls.

## Screenshots

Place final screenshots in `docs/assets/screenshots/`.

- API docs placeholder: `docs/assets/screenshots/api-docs.png`
- Streamlit query placeholder: `docs/assets/screenshots/streamlit-query.png`
- Evaluation metrics placeholder: `docs/assets/screenshots/evaluation-report.png`

## Security

This repository is designed for public portfolio use:

- no real PII;
- no production data;
- no hardcoded API keys;
- mock mode for tests and demos;
- `.env` ignored by git;
- CodeQL and Dependabot configured.

See [docs/security.md](docs/security.md).

## Cost Control

The default mock mode costs `$0`. Optional OpenAI usage is opt-in and should be capped through provider/project controls.

See [docs/cost-control.md](docs/cost-control.md).

## Docker

```powershell
docker compose up --build
```

- API: http://localhost:8000
- UI: http://localhost:8501

No secrets are baked into the image. Use environment variables or local `.env` files for optional API-backed usage.

## Limitations

- V1 supports Markdown and TXT documents. PDF ingestion is documented as a future extension.
- The local vector store is a small JSON-backed abstraction for reproducibility, not a high-scale database.
- Mock answer generation is deterministic and intentionally simple.
- Groundedness is heuristic, not a substitute for human review or model-graded evaluation.
- Guardrails reduce obvious misuse but do not guarantee safety.

See [docs/limitations.md](docs/limitations.md).

## Roadmap

- PDF parsing with careful dependency selection.
- ChromaDB or pgvector adapter behind the existing vector-store interface.
- Model-graded evaluation with strict cost controls.
- Authentication and per-user rate limiting for hosted deployments.
- ADRs for architecture changes.
- Screenshot capture and UI polish after first public release.

## Conventional Commits

Use Conventional Commits for release automation:

- `feat: add pdf ingestion adapter`
- `fix: tighten citation guardrail`
- `docs: update cost control guidance`
- `test: add retrieval regression cases`

## CV Bullets

- Built a local-first enterprise RAG compliance assistant with FastAPI, deterministic embeddings, vector retrieval, cited answers, guardrails, SQLite traces, and Streamlit UI.
- Implemented evaluation harness measuring retrieval hit rate, source match accuracy, citation presence, refusal behavior, groundedness heuristic, and answer length sanity.
- Designed pluggable mock/OpenAI provider architecture so tests run without paid API usage while production-style configuration remains available.
- Added CI/CD, Docker, CodeQL, Dependabot, release automation scaffolding, bilingual docs, and public-repo security/cost controls.

## Interview Explanation

This project demonstrates how I build GenAI systems as engineering products, not demos. The assistant retrieves from a controlled policy corpus, answers only with cited context, refuses unsupported questions, logs traces, and includes an evaluation harness so behavior can be measured over time. Mock providers make the system reproducible and free to test, while provider interfaces allow OpenAI-backed execution when configured. The documentation explains security, costs, limitations, and deployment tradeoffs so reviewers can assess both implementation and engineering judgment.
