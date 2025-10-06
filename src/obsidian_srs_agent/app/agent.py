"""High-level orchestration for the Obsidian SRS agent."""
from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass
from typing import Any, Optional, TYPE_CHECKING

from .baml_client import CardGenerator
from .models import Card, CardGenControls, SourceDoc, WriteResult
from .tools import (
    chunk_document,
    fetch_and_extract_jina,
    generate_cards,
    strands_fetch_and_extract,
    strands_generate_cards,
    strands_write_obsidian,
    write_obsidian,
)

if TYPE_CHECKING:  # pragma: no cover - typing aid only
    from strands import Agent as StrandsAgentType
else:  # pragma: no cover - runtime fallback
    StrandsAgentType = Any

try:  # pragma: no cover - exercised when strands is available
    from strands import Agent as _StrandsAgent
except ImportError:  # pragma: no cover - fallback for environments without strands
    _StrandsAgent = None

StrandsAgent = _StrandsAgent

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineConfig:
    vault_path: str
    domain: str
    topic: str
    url: Optional[str] = None
    raw_text: Optional[str] = None
    num_cards: int = 10
    difficulty: Optional[str] = None
    focus_area: Optional[str] = None
    style: Optional[str] = None
    file_basename: Optional[str] = None
    force_baml: bool = False


@dataclass(slots=True)
class PipelinePreview:
    """Snapshot of generated cards ready for user confirmation."""

    cards: list[Card]
    source: SourceDoc
    controls: CardGenControls
    model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None


class ObsidianSRSAgent:
    """Sequential pipeline that mirrors the behaviour of the Strands agent."""

    def __init__(self, *, generator: Optional[CardGenerator] = None) -> None:
        self._generator = generator or CardGenerator()
        self._strands_agent: Optional[StrandsAgentType] = None

    def generate(self, config: PipelineConfig) -> PipelinePreview:
        request_id = uuid.uuid4().hex
        LOGGER.info("Starting request %s", request_id)
        source = self._prepare_source(config)

        controls = CardGenControls(
            num_cards=config.num_cards,
            difficulty=config.difficulty,
            focus_area=config.focus_area,
            style=config.style,
        )

        generator = self._generator if not config.force_baml else CardGenerator(force_baml=True)

        chunks = chunk_document(source)
        LOGGER.info("Processing %s chunk(s) for request %s", len(chunks), request_id)
        combined_cards: list[Card] = []
        meta_model: Optional[str] = None
        prompt_tokens: Optional[int] = None
        completion_tokens: Optional[int] = None
        for chunk in chunks:
            result = generate_cards(
                doc=chunk,
                controls=controls,
                generator=generator,
                force_baml=config.force_baml,
            )
            if result.model:
                meta_model = result.model
            if result.prompt_tokens:
                prompt_tokens = (prompt_tokens or 0) + result.prompt_tokens
            if result.completion_tokens:
                completion_tokens = (completion_tokens or 0) + result.completion_tokens
            combined_cards.extend(result.cards)
            if len(combined_cards) >= controls.num_cards:
                break
        combined_cards = combined_cards[: controls.num_cards]

        LOGGER.info(
            "Generated %s cards for request %s", len(combined_cards), request_id
        )
        return PipelinePreview(
            cards=combined_cards,
            source=source,
            controls=controls,
            model=meta_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    def write(self, preview: PipelinePreview, config: PipelineConfig) -> WriteResult:
        write_result = write_obsidian(
            vault_root=config.vault_path,
            cards=preview.cards,
            source_title=preview.source.title,
            source_url=preview.source.url,
            domain=config.domain,
            topic=config.topic,
            file_basename=config.file_basename,
        )

        LOGGER.info(
            "Completed write with %s cards -> %s",
            len(preview.cards),
            write_result.path,
        )
        return write_result

    def run(self, config: PipelineConfig) -> WriteResult:
        preview = self.generate(config)
        return self.write(preview, config)

    def _prepare_source(self, config: PipelineConfig) -> SourceDoc:
        if config.url:
            return fetch_and_extract_jina(config.url)
        if config.raw_text:
            return SourceDoc(text=config.raw_text)
        raise ValueError("Either url or raw_text must be provided.")

    # ------------------------------------------------------------------
    # Strands integration helpers
    # ------------------------------------------------------------------
    def create_strands_agent(
        self,
        *,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> StrandsAgentType:
        """Expose a ready-to-use Strands agent that can orchestrate the tools."""

        if StrandsAgent is None:  # pragma: no cover - exercised when strands missing
            raise RuntimeError(
                "strands-agents is not installed. Install it to enable agent mode."
            )

        if self._strands_agent is not None and model is None and system_prompt is None:
            return self._strands_agent

        prompt = system_prompt or (
            "You are an orchestration agent that extracts content, generates flashcards, "
            "and writes them into an Obsidian vault using the provided tools. Always call "
            "fetch_and_extract_jina first when a URL is available, otherwise operate on "
            "raw text. Afterwards call generate_cards and finally write_obsidian."
        )

        resolved_model = model
        if resolved_model is None:
            resolved_model = os.getenv("SR_STRANDS_MODEL") or None

        agent = StrandsAgent(
            model=resolved_model,
            tools=[
                strands_fetch_and_extract,
                strands_generate_cards,
                strands_write_obsidian,
            ],
            system_prompt=prompt,
        )

        if model is None and system_prompt is None:
            self._strands_agent = agent
        return agent
