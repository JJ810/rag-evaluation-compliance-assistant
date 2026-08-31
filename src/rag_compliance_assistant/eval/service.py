from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rag_compliance_assistant.config import Settings
from rag_compliance_assistant.eval.metrics import (
    EvaluationCase,
    aggregate_case_metrics,
    evaluate_answer,
)
from rag_compliance_assistant.rag.service import RagService


class EvaluationService:
    def __init__(self, settings: Settings, rag_service: RagService) -> None:
        self._settings = settings
        self._rag_service = rag_service

    def load_cases(self, dataset_path: Path | None = None) -> list[EvaluationCase]:
        path = dataset_path or self._settings.eval_sets_dir / "synthetic_compliance_eval.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [
            EvaluationCase(
                id=str(item["id"]),
                query=str(item["query"]),
                expected_sources=list(item.get("expected_sources", [])),
                should_refuse=bool(item.get("should_refuse", False)),
                notes=str(item.get("notes", "")),
            )
            for item in payload["cases"]
        ]

    def run(
        self,
        *,
        dataset_path: Path | None = None,
        report_path: Path | None = None,
        top_k: int | None = None,
    ) -> dict[str, Any]:
        cases = self.load_cases(dataset_path)
        case_results: list[dict[str, Any]] = []
        for case in cases:
            result = self._rag_service.ask(
                case.query,
                top_k=top_k,
                evaluation_case_id=case.id,
            )
            case_results.append(evaluate_answer(case, result))

        aggregate = aggregate_case_metrics(case_results)
        report = {
            "schema_version": 1,
            "generated_at": datetime.now(UTC).isoformat(),
            "dataset": str(
                dataset_path or self._settings.eval_sets_dir / "synthetic_compliance_eval.json"
            ),
            "providers": {
                "llm": self._settings.llm_provider,
                "embedding": self._settings.embedding_provider,
            },
            "metrics": aggregate,
            "cases": case_results,
        }
        output_path = report_path or self._settings.eval_report_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return report
