FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md VERSION ./
COPY src ./src
COPY data/sample_docs ./data/sample_docs
COPY data/eval_sets ./data/eval_sets

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -e .

RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/data/vector_store /app/data/traces /app/reports/eval \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "rag_compliance_assistant.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
