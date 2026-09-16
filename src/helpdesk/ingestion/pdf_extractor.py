from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from helpdesk.errors import KnowledgeBaseError
from helpdesk.ingestion.models import PageText


def normalize_text(text: str) -> str:
    """Normalize extraction artifacts while preserving paragraph boundaries."""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf(path: Path) -> list[PageText]:
    """Extract non-empty page text from a readable PDF."""
    try:
        reader = PdfReader(path)
        if reader.is_encrypted:
            try:
                if not reader.decrypt(""):
                    raise KnowledgeBaseError(f"PDF is encrypted: {path.name}")
            except Exception as exc:
                raise KnowledgeBaseError(f"PDF is encrypted: {path.name}") from exc
        pages: list[PageText] = []
        for number, page in enumerate(reader.pages, start=1):
            text = normalize_text(page.extract_text() or "")
            if text:
                pages.append(PageText(source=path.name, page=number, text=text))
        if not pages:
            raise KnowledgeBaseError(f"No extractable text was found in {path.name}.")
        return pages
    except KnowledgeBaseError:
        raise
    except (PdfReadError, OSError, ValueError) as exc:
        raise KnowledgeBaseError(f"Could not read PDF: {path.name}", str(exc)) from exc


def extract_directory(directory: Path) -> list[PageText]:
    """Extract every PDF in a directory in deterministic filename order."""
    if not directory.exists():
        raise KnowledgeBaseError(f"Knowledge-base directory does not exist: {directory}")
    paths = sorted(directory.glob("*.pdf"))
    if not paths:
        raise KnowledgeBaseError(f"No PDF documents were found in {directory}")
    pages: list[PageText] = []
    for path in paths:
        pages.extend(extract_pdf(path))
    return pages
