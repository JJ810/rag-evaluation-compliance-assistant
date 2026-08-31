from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rag_compliance_assistant.config import Settings
from rag_compliance_assistant.observability.traces import TraceStore


class MetricsService:
    def __init__(self, settings: Settings, trace_store: TraceStore) -> None:
        self._settings = settings
        self._trace_store = trace_store

    def snapshot(self) -> dict[str, Any]:
        evaluation_report = self._read_latest_eval_report(self._settings.eval_report_path)
        return {
            "app": {
                "name": self._settings.app_name,
                "version": self._settings.app_version,
                "environment": self._settings.environment,
            },
            "providers": {
                "llm": self._settings.llm_provider,
                "embedding": self._settings.embedding_provider,
            },
            "traces": self._trace_store.summary(),
            "latest_evaluation": evaluation_report,
        }

    def _read_latest_eval_report(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        return {
            "generated_at": payload.get("generated_at"),
            "dataset": payload.get("dataset"),
            "metrics": payload.get("metrics"),
        }
