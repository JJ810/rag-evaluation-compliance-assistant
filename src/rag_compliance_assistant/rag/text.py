from __future__ import annotations

import re

TOKEN_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]*")
STOPWORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "must",
    "of",
    "on",
    "or",
    "our",
    "should",
    "the",
    "to",
    "what",
    "when",
    "where",
    "who",
    "with",
}


def tokenize(text: str, *, remove_stopwords: bool = False) -> list[str]:
    tokens = [match.group(0).lower() for match in TOKEN_RE.finditer(text)]
    if remove_stopwords:
        return [token for token in tokens if token not in STOPWORDS and len(token) > 1]
    return tokens


def content_terms(text: str) -> set[str]:
    return set(tokenize(text, remove_stopwords=True))


def count_overlap(query: str, text: str) -> int:
    return len(content_terms(query) & content_terms(text))
