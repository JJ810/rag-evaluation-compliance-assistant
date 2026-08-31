from __future__ import annotations

import re

from rag_compliance_assistant.domain.models import RetrievedChunk
from rag_compliance_assistant.rag.text import content_terms


def citation_marker(result: RetrievedChunk) -> str:
    return f"[{result.chunk.source}#chunk-{result.chunk.chunk_index}]"


def select_supporting_sentence(query: str, text: str) -> str | None:
    """Select a concise sentence from a chunk that best supports the query."""

    query_terms = content_terms(query)
    candidates: list[tuple[int, int, str]] = []
    fallback: str | None = None
    for index, sentence in enumerate(split_sentences(text)):
        cleaned = clean_policy_sentence(sentence)
        if not cleaned or _is_low_value_sentence(cleaned):
            continue
        fallback = fallback or cleaned
        overlap = len(query_terms & content_terms(cleaned))
        candidates.append((overlap, -index, cleaned))

    if not candidates:
        return fallback

    candidates.sort(reverse=True)
    best_overlap, _, best_sentence = candidates[0]
    if best_overlap == 0:
        return fallback
    return best_sentence


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def clean_policy_sentence(sentence: str) -> str:
    cleaned = re.sub(r"#+\s*", " ", sentence)
    cleaned = re.sub(r"\b(Purpose|Requirements|Evidence)\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" -")


def _is_low_value_sentence(sentence: str) -> bool:
    lowered = sentence.lower()
    return "synthetic policy" in lowered or lowered in {
        "access control policy",
        "approved ai usage policy",
        "data retention policy",
        "incident response policy",
        "vendor risk management policy",
    }
