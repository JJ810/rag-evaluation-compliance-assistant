from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from rag_compliance_assistant.domain.models import AnswerResult, RetrievedChunk
from rag_compliance_assistant.rag.text import STOPWORDS, tokenize


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    query: str
    expected_sources: list[str]
    should_refuse: bool = False
    notes: str = ""


def source_hit_at_k(retrieved_chunks: list[RetrievedChunk], expected_sources: list[str]) -> bool:
    if not expected_sources:
        return False
    retrieved_sources = {result.chunk.source for result in retrieved_chunks}
    return any(expected in retrieved_sources for expected in expected_sources)


def source_match_accuracy(
    retrieved_chunks: list[RetrievedChunk],
    expected_sources: list[str],
) -> float:
    if not expected_sources:
        return 1.0
    retrieved_sources = {result.chunk.source for result in retrieved_chunks}
    matches = sum(1 for expected in expected_sources if expected in retrieved_sources)
    return matches / len(expected_sources)


def has_citation_markers(answer: str) -> bool:
    return bool(re.search(r"\[[^\]]+\.md#chunk-\d+\]", answer))


def refused(answer: str) -> bool:
    return "do not have enough evidence" in answer.lower()


def answer_length_sane(answer: str, *, min_words: int = 8, max_words: int = 180) -> bool:
    word_count = len(tokenize(answer))
    return min_words <= word_count <= max_words


def groundedness_score(answer: str, context: str) -> float:
    """Approximate groundedness by checking answer content terms against context terms."""

    answer_terms = {
        token
        for token in tokenize(re.sub(r"\[[^\]]+\]", "", answer), remove_stopwords=True)
        if token not in STOPWORDS
    }
    if not answer_terms:
        return 1.0
    context_terms = set(tokenize(context, remove_stopwords=True))
    supported = answer_terms & context_terms
    return len(supported) / len(answer_terms)


def evaluate_answer(case: EvaluationCase, result: AnswerResult) -> dict[str, Any]:
    context = " ".join(retrieved.chunk.text for retrieved in result.retrieved_chunks)
    refused_answer = refused(result.answer)
    return {
        "case_id": case.id,
        "query": case.query,
        "expected_sources": case.expected_sources,
        "retrieved_sources": [retrieved.chunk.source for retrieved in result.retrieved_chunks],
        "hit_at_k": source_hit_at_k(result.retrieved_chunks, case.expected_sources),
        "source_match_accuracy": source_match_accuracy(
            result.retrieved_chunks,
            case.expected_sources,
        ),
        "citation_present": has_citation_markers(result.answer) if not case.should_refuse else True,
        "groundedness_score": groundedness_score(result.answer, context),
        "refusal_expected": case.should_refuse,
        "refusal_observed": refused_answer,
        "refusal_correct": refused_answer == case.should_refuse,
        "answer_length_sane": answer_length_sane(result.answer),
        "confidence": result.confidence,
        "guardrail_decision": result.guardrail.decision,
    }


def aggregate_case_metrics(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(case_results)
    if total == 0:
        return {
            "cases": 0,
            "retrieval_hit_rate": 0.0,
            "mean_source_match_accuracy": 0.0,
            "citation_presence_rate": 0.0,
            "mean_groundedness_score": 0.0,
            "refusal_accuracy": 0.0,
            "answer_length_sanity_rate": 0.0,
        }

    retrieval_cases = [case for case in case_results if case["expected_sources"]]
    citation_cases = [case for case in case_results if not case["refusal_expected"]]
    return {
        "cases": total,
        "retrieval_hit_rate": _mean([case["hit_at_k"] for case in retrieval_cases]),
        "mean_source_match_accuracy": _mean(
            [case["source_match_accuracy"] for case in retrieval_cases]
        ),
        "citation_presence_rate": _mean([case["citation_present"] for case in citation_cases]),
        "mean_groundedness_score": _mean([case["groundedness_score"] for case in case_results]),
        "refusal_accuracy": _mean([case["refusal_correct"] for case in case_results]),
        "answer_length_sanity_rate": _mean([case["answer_length_sane"] for case in case_results]),
    }


def _mean(values: list[bool | float]) -> float:
    if not values:
        return 0.0
    numeric = [
        1.0 if value is True else 0.0 if value is False else float(value) for value in values
    ]
    return sum(numeric) / len(numeric)
