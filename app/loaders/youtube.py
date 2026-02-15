"""Helpers for loading transcript text from YouTube URLs."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi


def _extract_video_id(url: str) -> str:
    """Extract a YouTube video ID from common URL formats."""
    parsed = urlparse(url)

    if parsed.hostname in {"youtu.be"}:
        return parsed.path.lstrip("/")

    if parsed.hostname in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            query = parse_qs(parsed.query)
            if "v" in query and query["v"]:
                return query["v"][0]
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/shorts/")[-1].split("/")[0]

    # Last fallback: try to match an 11-char ID anywhere in the URL.
    match = re.search(r"([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)

    msg = "Could not find a YouTube video ID in the provided URL."
    raise ValueError(msg)


def load_youtube_transcript(url: str) -> str:
    """Download transcript and merge all caption snippets into one text block."""
    video_id = _extract_video_id(url)
    transcript_items = YouTubeTranscriptApi.get_transcript(video_id)
    return "\n".join(item["text"].strip() for item in transcript_items if item.get("text"))
