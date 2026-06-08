# Enterprise RAG Evaluation & Compliance Assistant

Proyecto local-first de GenAI/RAG para portafolio profesional. Muestra ingenieria de IA aplicada, evaluacion, guardrails, observabilidad, diseno de APIs, seguridad, control de costos, CI/CD y documentacion bilingue.

No es un chatbot generico. Es un sistema RAG orientado a cumplimiento: recupera evidencia desde politicas locales sinteticas, genera respuestas con citas, rechaza preguntas sin soporte documental, registra trazas y ejecuta evaluaciones reproducibles.

## Que Demuestra

- Backend FastAPI con endpoints de salud, ingesta, consulta, evaluacion, metricas y trazas.
- Pipeline RAG deterministico con documentos locales, chunking, embeddings, busqueda vectorial, citas y metadatos de fuente.
- Proveedores intercambiables: mock gratuito por defecto y OpenAI opcional cuando `OPENAI_API_KEY` esta configurada.
- Evaluacion de hit@k, precision de fuente, presencia de citas, groundedness heuristico, rechazos y longitud de respuesta.
- Guardrails simples y testeables contra prompt injection, solicitudes de secretos, preguntas fuera de alcance y respuestas sin citas.
- Trazas locales en SQLite y UI minima en Streamlit.
- Pytest, ruff, mypy, cobertura, pre-commit, Docker, GitHub Actions, CodeQL, Dependabot y Release Please.

## Arquitectura

```text
Documentos -> Loader -> Chunks -> Embeddings -> Vector store local
Pregunta -> Guardrails -> Retrieval -> LLM provider -> Respuesta citada -> Trazas
Eval set -> Servicio RAG -> Metricas -> Reporte JSON
```

Mas detalle en [docs/architecture.md](docs/architecture.md).

## Como Funciona RAG en Modo Mock Sin API Keys

La configuracion por defecto `mock/mock` ejecuta un flujo RAG local y deterministico:

1. carga politicas Markdown/TXT desde `data/sample_docs`;
2. divide documentos en chunks estables;
3. `MockEmbeddingProvider` genera embeddings deterministas sin llamadas de red;
4. el vector store local en JSON ordena chunks con similitud coseno;
5. filtra chunks de baja relevancia antes de mostrar citas y evidencia;
6. `MockLLMProvider` selecciona la frase de politica mas relevante y genera una respuesta breve con cita;
7. los guardrails validan citas, rechazos y solicitudes inseguras obvias;
8. las trazas se guardan localmente en SQLite.

Por eso pruebas, CI, demos locales y Docker no requieren `OPENAI_API_KEY` ni generan costo. El modo OpenAI es opcional y solo se activa con variables de entorno explicitas.

## Instalacion Local

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Por defecto usa proveedores mock y no requiere credenciales cloud.

Modo OpenAI opcional:

```bash
cp .env.example .env
# configurar OPENAI_API_KEY, EMBEDDING_PROVIDER=openai, LLM_PROVIDER=openai
```

Nunca subir `.env` ni llaves reales.

## Comandos

Targets con GNU Make, si esta disponible:

```bash
make ingest
make eval
make api
make ui
make lint
make type
make test
make docker-up
```

Comandos directos para Windows PowerShell:

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

## API

```powershell
curl.exe http://127.0.0.1:8000/health
curl.exe -X POST http://127.0.0.1:8000/ingest
curl.exe -X POST http://127.0.0.1:8000/query `
  -H "Content-Type: application/json" `
  -d '{"query":"Can employees paste confidential customer data into unapproved public AI tools?","top_k":4}'
curl.exe -X POST http://127.0.0.1:8000/evaluate -H "Content-Type: application/json" -d '{"top_k":4}'
curl.exe http://127.0.0.1:8000/traces
curl.exe http://127.0.0.1:8000/metrics
```

## Seguridad y Costos

El modo por defecto cuesta `$0`, no usa datos reales, no guarda secretos y no requiere API keys. El modo OpenAI es opt-in y debe usarse con limites de presupuesto.

Ver [docs/security.md](docs/security.md) y [docs/cost-control.md](docs/cost-control.md).

## Limitaciones

- V1 soporta Markdown/TXT; PDF queda como extension futura.
- El vector store local en JSON es para demos reproducibles, no para escala enterprise.
- La evaluacion de groundedness es heuristica.
- Los guardrails no son controles de seguridad perfectos.

## Bullets para CV

- Construyo un asistente RAG local-first con FastAPI, busqueda vectorial, respuestas citadas, guardrails, trazas SQLite y UI Streamlit.
- Implemente evaluacion reproducible para retrieval, citas, groundedness heuristico y rechazos.
- Disene arquitectura pluggable mock/OpenAI para pruebas sin costo y ejecucion API-backed opcional.
- Agregue Docker, CI/CD, CodeQL, Dependabot, documentacion bilingue y controles de seguridad/costos para repo publico.
