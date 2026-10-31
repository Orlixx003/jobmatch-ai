"""Extract plain text from a CV file (PDF, DOCX, TXT or MD)."""

from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO

SUPPORTED = {".pdf", ".docx", ".txt", ".md"}


class CVReadError(ValueError):
    """Raised when a CV cannot be read."""


def _read_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _read_docx(data: bytes) -> str:
    from docx import Document

    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)


def read_cv(source: str | Path | BinaryIO, filename: str | None = None) -> str:
    """Return the text of a CV.

    `source` can be a path or a file-like object (e.g. a Streamlit upload).
    When passing a file-like object, give `filename` so the type is known.
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        filename = filename or path.name
        data = path.read_bytes()
    else:
        data = source.read()
        filename = filename or getattr(source, "name", "")

    suffix = Path(filename or "").suffix.lower()
    if suffix not in SUPPORTED:
        raise CVReadError(f"Unsupported file type '{suffix}'. Use: {', '.join(sorted(SUPPORTED))}")

    try:
        if suffix == ".pdf":
            text = _read_pdf(data)
        elif suffix == ".docx":
            text = _read_docx(data)
        else:
            text = data.decode("utf-8", errors="replace")
    except Exception as exc:
        raise CVReadError(f"Could not read {filename}: {exc}") from exc

    text = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if len(text) < 50:
        raise CVReadError("The CV looks empty. If it is a scanned PDF, export it as text first.")
    return text
