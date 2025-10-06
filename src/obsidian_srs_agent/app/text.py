"""Lightweight text helpers used by the agent."""
from __future__ import annotations

import re
from typing import Iterable, List

SENTENCE_END_RE = re.compile(r"(?<=[.!?]) +")


def normalize_text(text: str) -> str:
    """Normalise whitespace and strip extraneous characters."""

    collapsed = re.sub(r"\s+", " ", text).strip()
    return collapsed


def split_sentences(text: str, *, max_length: int = 280) -> List[str]:
    """Split text into reasonably sized sentences."""

    normalized = normalize_text(text)
    if not normalized:
        return []
    parts = SENTENCE_END_RE.split(normalized)
    sentences: List[str] = []
    buffer: List[str] = []
    length = 0
    for part in parts:
        if length + len(part) <= max_length:
            buffer.append(part)
            length += len(part)
        else:
            sentences.append(" ".join(buffer).strip())
            buffer = [part]
            length = len(part)
    if buffer:
        sentences.append(" ".join(buffer).strip())
    return [sentence for sentence in sentences if sentence]


def extract_key_points(text: str, *, limit: int = 12) -> List[str]:
    """Extract key sentences from the source text."""

    sentences = split_sentences(text)
    if len(sentences) <= limit:
        return sentences
    stride = max(1, len(sentences) // limit)
    return sentences[::stride][:limit]


def ensure_min_length(chunks: Iterable[str]) -> List[str]:
    """Filter out tiny chunks that offer little value."""

    return [chunk for chunk in chunks if len(chunk.strip()) > 20]
