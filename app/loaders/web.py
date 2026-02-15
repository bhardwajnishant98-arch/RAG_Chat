"""Helpers for loading and cleaning text content from websites."""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup


def load_webpage_text(url: str, timeout: int = 15) -> str:
    """Fetch URL content and return readable page text.

    This intentionally uses a simple and beginner-friendly approach:
    - download the page
    - remove script/style tags
    - extract visible text
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(cleaned_lines)
