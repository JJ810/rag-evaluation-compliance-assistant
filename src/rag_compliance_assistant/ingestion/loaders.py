from __future__ import annotations

import hashlib
import re
from pathlib import Path

from rag_compliance_assistant.domain.models import Document

SUPPORTED_EXTENSIONS = {".md", ".txt"}


def stable_document_id(source: str, text: str) -> str:
    digest = hashlib.sha1(f"{source}\n{text}".encode()).hexdigest()
    return f"doc_{digest[:12]}"


def extract_title(path: Path, text: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+)$", line.strip())
        if match:
            return match.group(1).strip()
    return path.stem.replace("_", " ").replace("-", " ").title()


def load_documents(directory: Path) -> list[Document]:
    """Load Markdown and text documents from a local directory."""

    if not directory.exists():
        raise FileNotFoundError(f"Document directory does not exist: {directory}")

    documents: list[Document] = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        source = path.name
        documents.append(
            Document(
                id=stable_document_id(source, text),
                source=source,
                title=extract_title(path, text),
                text=text,
                metadata={
                    "path": str(path),
                    "extension": path.suffix.lower(),
                },
            )
        )
    return documents
