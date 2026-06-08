# Deployment

## Local Development

Install:

```powershell
python -m pip install -e ".[dev]"
```

Run API on Windows PowerShell:

```powershell
python -m uvicorn rag_compliance_assistant.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Run UI on Windows PowerShell:

```powershell
python -m streamlit run src\rag_compliance_assistant\ui\app.py
```

The same commands work on macOS/Linux with `/` path separators for the UI path.

## Docker Compose

```bash
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- UI: `http://localhost:8501`

The compose file uses mock providers by default and stores generated runtime artifacts in Docker volumes.

Docker Compose does not require `OPENAI_API_KEY` in the default configuration.

## Environment Variables

Important variables:

- `EMBEDDING_PROVIDER`: `mock` or `openai`
- `LLM_PROVIDER`: `mock` or `openai`
- `OPENAI_API_KEY`: required only for OpenAI mode
- `OPENAI_EMBEDDING_MODEL`
- `OPENAI_CHAT_MODEL`
- `VECTOR_STORE_PATH`
- `TRACE_DB_PATH`
- `EVAL_REPORT_PATH`

Tests and CI should keep `EMBEDDING_PROVIDER=mock` and `LLM_PROVIDER=mock` so they never depend on external credentials or paid API usage.

## Hosted Deployment Considerations

Before deploying publicly:

- add authentication;
- add authorization for document collections;
- add request rate limits;
- add request body size limits;
- configure central logs and monitoring;
- configure budget alerts;
- store secrets in a managed secret store;
- review prompt injection and data exfiltration risks;
- replace synthetic docs with approved non-confidential documents only.

No real cloud resources are created by this repository.
