from __future__ import annotations

import re

from rag_compliance_assistant.domain.models import Citation, GuardrailResult


class GuardrailEngine:
    """Simple deterministic guardrails for portfolio-grade demos.

    These checks reduce obvious misuse in local demos; they are not complete
    security controls and should be paired with provider-side and platform controls.
    """

    _PROMPT_INJECTION_PATTERNS = [
        re.compile(pattern, re.IGNORECASE)
        for pattern in (
            r"ignore\s+(all\s+)?(previous|above|prior|system|developer)\s+instructions",
            r"ignore\s+.*\binstructions\b",
            r"disregard\s+(the\s+)?(previous|system|developer)\s+instructions",
            r"reveal\s+(the\s+)?(system|developer)\s+(prompt|message|instructions)",
            r"reveal\s+(the\s+)?prompt\b",
            r"jailbreak",
            r"prompt\s+injection",
        )
    ]
    _SECRET_PATTERNS = [
        re.compile(pattern, re.IGNORECASE)
        for pattern in (
            r"\b(api[_ -]?key|secret|password|credential|token)\b",
            r"\b(openai_api_key|aws_secret_access_key|private key)\b",
        )
    ]
    _OUT_OF_SCOPE_PATTERNS = [
        re.compile(pattern, re.IGNORECASE)
        for pattern in (
            r"\b(weather|sports score|stock price|recipe|movie recommendation)\b",
            r"\b(cafeteria|lunch menu)\b",
            r"\bmedical diagnosis\b",
            r"\binvestment advice\b",
            r"\bwrite\s+(a\s+)?(poem|song|novel)\b",
        )
    ]

    def check_query(self, query: str) -> GuardrailResult:
        reasons: list[str] = []
        if not query.strip():
            return GuardrailResult(
                allowed=False,
                decision="empty_query",
                reasons=["Query must not be empty."],
            )

        if any(pattern.search(query) for pattern in self._PROMPT_INJECTION_PATTERNS):
            reasons.append("Prompt injection pattern detected.")
        if any(pattern.search(query) for pattern in self._SECRET_PATTERNS):
            reasons.append("Request appears to ask for secrets or credentials.")
        if any(pattern.search(query) for pattern in self._OUT_OF_SCOPE_PATTERNS):
            reasons.append("Request is outside the compliance document assistant scope.")

        if reasons:
            return GuardrailResult(allowed=False, decision="blocked_query", reasons=reasons)
        return GuardrailResult(allowed=True, decision="allowed", reasons=[])

    def check_answer(
        self,
        answer: str,
        citations: list[Citation],
        *,
        required: bool,
    ) -> GuardrailResult:
        if required and not citations:
            return GuardrailResult(
                allowed=False,
                decision="missing_citations",
                reasons=["Answer was generated without citations."],
            )
        if required and not re.search(r"\[[^\]]+\.md#chunk-\d+\]", answer):
            return GuardrailResult(
                allowed=False,
                decision="missing_citation_markers",
                reasons=["Answer text does not include source citation markers."],
            )
        return GuardrailResult(allowed=True, decision="answer_allowed", reasons=[])
