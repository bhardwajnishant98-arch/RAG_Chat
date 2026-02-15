"""Helpers for extracting text from PDF files."""

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader


def load_pdf_text(file_bytes: bytes) -> str:
    """Extract text from all pages in a PDF represented as raw bytes."""
    reader = PdfReader(BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(page.strip() for page in pages if page.strip())
