import logging
import time
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Iterable, List, Optional

import requests
from slugify import slugify

from .baml_client import BAMLUnavailableError, CardGenerator, debug_dump_cards
from .models import (
    Card,
    CardGenControls,
    GenerationResult,
    SourceDoc,
    WriteResult,
)
from .vault import MarkdownVaultWriter

LOGGER = logging.getLogger(__name__)
USER_AGENT = "ObsidianSRS-Agent/0.1"
JINA_BASE_URL = "https://r.jina.ai/"
MAX_CHARS_PER_CHUNK = 7500
CHUNK_OVERLAP = 500
RETRY_STATUS = {429, 500, 502, 503, 504}


def fetch_and_extract_jina(url: str, *, timeout: int = 30) -> SourceDoc:
    """Fetch and extract article content via the public Jina reader."""

    session = requests.Session()
    headers = {"User-Agent": USER_AGENT}
    attempt = 0
    response: Optional[requests.Response] = None
    while attempt < 3:
        attempt += 1
        try:
            response = session.get(
                f"{JINA_BASE_URL}{url}", headers=headers, timeout=timeout
            )
        except requests.RequestException as exc:  # type: ignore[attr-defined]
            LOGGER.warning("Jina request failed on attempt %s: %s", attempt, exc)
            if attempt >= 3:
                raise
            time.sleep(2**attempt)
            continue

        if response.status_code in RETRY_STATUS:
            LOGGER.info("Retrying Jina fetch due to status %s", response.status_code)
            time.sleep(2**attempt)
            continue

        break

    if response is None:
        raise RuntimeError("Failed to obtain response from Jina Reader")

    if response.status_code >= 400:
        raise RuntimeError(
            f"Jina Reader returned {response.status_code}: {response.text[:200]}"
        )

    text = response.text
    title = _extract_title(text)
    return SourceDoc(text=text, title=title, url=url)


def _extract_title(markdown: str) -> Optional[str]:
    for line in markdown.splitlines():
        if line.startswith("#"):
            return line.lstrip("# ").strip()
    return None


def chunk_document(doc: SourceDoc) -> List[SourceDoc]:
    """Split a source document into chunks suitable for LLM processing."""

    text = doc.text
    if len(text) <= MAX_CHARS_PER_CHUNK:
        return [doc]

    chunks: List[SourceDoc] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + MAX_CHARS_PER_CHUNK)
        chunk_text = text[start:end]
        chunks.append(SourceDoc(text=chunk_text, title=doc.title, url=doc.url))
        if end == len(text):
            break
        start = max(0, end - CHUNK_OVERLAP)
    return chunks


def generate_cards(
    *,
    doc: SourceDoc,
    controls: CardGenControls,
    generator: Optional[CardGenerator] = None,
    force_baml: bool = False,
) -> GenerationResult:
    """Generate cards for the provided document."""

    generator = generator or CardGenerator(force_baml=force_baml)
    try:
        result = generator.generate(doc=doc, controls=controls)
    except BAMLUnavailableError:
        LOGGER.warning("BAML unavailable; falling back to heuristic generation")
        result = generator.generate(doc=doc, controls=controls, fallback=True)
    debug_dump_cards(result.cards)
    return result


def write_obsidian(
    *,
    vault_root: str,
    cards: Iterable[Card],
    source_title: Optional[str],
    source_url: Optional[str],
    domain: str,
    topic: str,
    file_basename: Optional[str] = None,
) -> WriteResult:
    writer = MarkdownVaultWriter(root=vault_root)
    deck_path = writer.write_cards(
        cards=list(cards),
        source_title=source_title,
        source_url=source_url,
        domain=domain,
        topic=topic,
        file_basename=file_basename,
    )
    return WriteResult(
        path=deck_path,
        created=datetime.now(timezone.utc).date(),
        deck_tag=f"#deck/{slugify(domain)}/{slugify(topic)}",
    )


try:  # pragma: no cover - exercised when strands is installed
    from strands import tool as strands_tool
except ImportError:  # pragma: no cover - fallback for environments without strands
    def strands_tool(*args, **kwargs):  # type: ignore[no-untyped-def]
        if args and callable(args[0]) and not kwargs:
            return args[0]

        def decorator(func):  # type: ignore[no-untyped-def]
            return func

        return decorator


@strands_tool(name="fetch_and_extract")
def strands_fetch_and_extract(url: str, timeout: int = 30) -> dict:
    """Strands wrapper returning JSON-serialisable payloads."""

    doc = fetch_and_extract_jina(url, timeout=timeout)
    return asdict(doc)


@strands_tool(name="generate_cards")
def strands_generate_cards(
    text: str,
    num_cards: int,
    difficulty: Optional[str] = None,
    focus_area: Optional[str] = None,
    style: Optional[str] = None,
    force_baml: bool = False,
) -> dict:
    """Generate cards through the same pipeline but return plain dicts."""

    source = SourceDoc(text=text)
    controls = CardGenControls(
        num_cards=num_cards,
        difficulty=difficulty,
        focus_area=focus_area,
        style=style,
    )
    generator = CardGenerator(force_baml=force_baml)
    result = generate_cards(
        doc=source,
        controls=controls,
        generator=generator,
        force_baml=force_baml,
    )
    return {
        "cards": [asdict(card) for card in result.cards],
        "model": result.model,
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
    }


@strands_tool(name="write_obsidian")
def strands_write_obsidian(
    vault_root: str,
    cards: List[dict],
    domain: str,
    topic: str,
    source_title: Optional[str] = None,
    source_url: Optional[str] = None,
    file_basename: Optional[str] = None,
) -> dict:
    """Write cards using JSON-compatible input for Strands orchestration."""

    card_objects = [
        Card(
            front=entry["front"],
            back=entry["back"],
            style=entry.get("style", "basic"),
            difficulty=entry.get("difficulty", "medium"),
            tags=list(entry.get("tags", [])),
        )
        for entry in cards
    ]
    result = write_obsidian(
        vault_root=vault_root,
        cards=card_objects,
        source_title=source_title,
        source_url=source_url,
        domain=domain,
        topic=topic,
        file_basename=file_basename,
    )
    return asdict(result)
