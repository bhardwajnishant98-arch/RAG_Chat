"""Helpers for extracting text from DOCX files."""

from __future__ import annotations

from io import BytesIO

from docx import Document


def load_docx_text(file_bytes: bytes) -> str:
    """Extract text from DOCX paragraphs represented as raw bytes."""
    document = Document(BytesIO(file_bytes))
    return "\n".join(p.text.strip() for p in document.paragraphs if p.text.strip())
