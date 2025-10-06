"""Thin wrapper around the optional BAML runtime."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from dataclasses import asdict
from typing import Iterable, List, Optional

import logging
import requests

from .models import Card, CardGenControls, GenerationResult, SourceDoc, ensure_card_styles
from .text import extract_key_points


LOGGER = logging.getLogger(__name__)
OPENAI_API_URL = os.getenv(
    "SR_OPENAI_ENDPOINT", "https://api.openai.com/v1/chat/completions"
)
DEFAULT_OPENAI_MODEL = os.getenv("SR_OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TIMEOUT = int(os.getenv("SR_OPENAI_TIMEOUT", "45"))


_BAML_SPEC = importlib.util.find_spec("baml") or importlib.util.find_spec("baml_gen")


class BAMLUnavailableError(RuntimeError):
    """Raised when BAML is required but not installed."""


def _load_baml_client():
    if _BAML_SPEC is None:
        raise BAMLUnavailableError(
            "BAML runtime is not installed. Install the 'baml' package to enable generation."
        )

    try:
        from baml import load  # type: ignore[import-not-found]

        project_root = Path(__file__).resolve().parents[2]
        config_path = project_root / "baml.yaml"
        return load(config_path)
    except ModuleNotFoundError:
        import importlib

        project_root = Path(__file__).resolve().parents[2]
        sys_path_added = False
        if str(project_root) not in sys.path:  # pragma: no cover - runtime safety
            sys.path.append(str(project_root))
            sys_path_added = True
        try:
            module = importlib.import_module("baml_gen.client")
        except ModuleNotFoundError as exc:
            raise BAMLUnavailableError(
                "BAML python client not found. Run `baml build` to generate baml_gen." \
                " If BAML is installed, ensure it is available on PYTHONPATH."
            ) from exc
        finally:
            if sys_path_added:
                sys.path.remove(str(project_root))
        return module


class CardGenerator:
    """Adapter that uses BAML when available and falls back to heuristics otherwise."""

    def __init__(self, force_baml: bool = False) -> None:
        self._force_baml = force_baml
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            self._client = _load_baml_client()
        return self._client

    def generate(
        self, *,
        doc: SourceDoc,
        controls: CardGenControls,
        fallback: bool = False,
    ) -> GenerationResult:
        """Generate cards from the provided document."""

        if _BAML_SPEC is None and not fallback and self._force_baml:
            raise BAMLUnavailableError("BAML runtime is required but missing.")

        if (_BAML_SPEC is None or fallback) and not self._force_baml:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and not fallback:
                try:
                    cards, meta = self._openai_generate(
                        api_key=api_key, doc=doc, controls=controls
                    )
                    return GenerationResult(
                        cards=cards,
                        model=meta.get("model"),
                        prompt_tokens=meta.get("prompt_tokens"),
                        completion_tokens=meta.get("completion_tokens"),
                    )
                except Exception as exc:  # noqa: BLE001
                    LOGGER.warning("OpenAI generation failed: %s", exc)

            cards = self._fallback_generate(doc=doc, controls=controls)
            return GenerationResult(cards=cards, model="heuristic")

        client = self._ensure_client()
        payload = client.cards.GenerateSRS(  # type: ignore[attr-defined]
            doc=asdict(doc),
            controls=asdict(controls),
        )
        cards = [
            Card(
                front=entry["front"],
                back=entry["back"],
                tags=entry.get("tags", []),
                style=entry.get("style", controls.style or "basic"),
                difficulty=entry.get("difficulty", controls.difficulty or "medium"),
            )
            for entry in payload
        ]
        cards = ensure_card_styles(cards, controls.style)
        meta = getattr(payload, "_raw_response", None)
        prompt_tokens = getattr(meta, "prompt_tokens", None) if meta else None
        completion_tokens = getattr(meta, "completion_tokens", None) if meta else None
        model = getattr(meta, "model", None) if meta else None
        return GenerationResult(
            cards=cards,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    def _fallback_generate(
        self, *, doc: SourceDoc, controls: CardGenControls
    ) -> List[Card]:
        """Fallback generator used when BAML or network access is unavailable."""

        sentences = extract_key_points(doc.text)
        max_cards = controls.num_cards if controls.num_cards > 0 else 1
        selected = sentences[:max_cards]
        tags: List[str] = []
        if controls.focus_area:
            tags.append(controls.focus_area)
        cards: List[Card] = []
        for sentence in selected:
            front = sentence
            back = sentence
            if (controls.style or "basic") == "reversed":
                front, back = back, front
            elif (controls.style or "basic") == "cloze":
                back = f"{{{{c1::{sentence}}}}}"
            cards.append(
                Card(
                    front=front,
                    back=back,
                    style=controls.style or "basic",
                    difficulty=controls.difficulty or "medium",
                    tags=list(tags),
                )
            )
        return cards

    def _openai_generate(
        self,
        *,
        api_key: str,
        doc: SourceDoc,
        controls: CardGenControls,
    ) -> tuple[List[Card], dict]:
        """Generate cards via the OpenAI API when BAML is unavailable."""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        style = controls.style or "basic"
        schema = {
            "type": "object",
            "properties": {
                "cards": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "front": {"type": "string"},
                            "back": {"type": "string"},
                            "style": {
                                "type": "string",
                                "enum": ["basic", "reversed", "cloze"],
                            },
                            "difficulty": {
                                "type": "string",
                                "enum": ["easy", "medium", "hard"],
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["front", "back"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["cards"],
            "additionalProperties": False,
        }
        focus_hint = (
            f"Focus on {controls.focus_area}. " if controls.focus_area else ""
        )
        style_hint = {
            "basic": "Use standard question::answer cards.",
            "reversed": "Return cards where the back should be treated as the answer and render using 'Question:::Answer'.",
            "cloze": "Use exactly one cloze deletion per card formatted as {{c1::...}}.",
        }[style]
        instructions = (
            "You are an assistant that creates high quality spaced repetition flashcards "
            "for Obsidian's Spaced Repetition plugin. Produce concise, factual prompts "
            "that capture one atomic idea each."
        )
        user_prompt = (
            f"Source title: {doc.title or 'Untitled'}\n"
            f"Source URL: {doc.url or 'n/a'}\n"
            f"Requested difficulty: {controls.difficulty or 'medium'}\n"
            f"Requested style: {style}. {style_hint}\n"
            f"{focus_hint}Generate up to {controls.num_cards} cards "
            "without inventing information beyond the provided text."
            " Return empty array if insufficient content.\n\n"
            f"Content:\n{doc.text[:12000]}"
        )

        payload = {
            "model": DEFAULT_OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": instructions},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "card_generation",
                    "schema": schema,
                    "strict": True,
                },
            },
            "temperature": 0.2,
            "max_tokens": max(controls.num_cards * 180, 400),
        }
        response = requests.post(
            OPENAI_API_URL, headers=headers, json=payload, timeout=OPENAI_TIMEOUT
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"OpenAI API error {response.status_code}: {response.text[:200]}"
            )

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:  # noqa: PERF203
            raise RuntimeError("Unexpected OpenAI response structure") from exc

        parsed = json.loads(content)
        cards_payload = parsed.get("cards", [])
        cards = [
            Card(
                front=entry.get("front", "").strip(),
                back=entry.get("back", "").strip(),
                style=entry.get("style", style),
                difficulty=entry.get("difficulty", controls.difficulty or "medium"),
                tags=list(entry.get("tags", [])),
            )
            for entry in cards_payload
            if entry.get("front") and entry.get("back")
        ]
        cards = ensure_card_styles(cards, controls.style)
        usage = data.get("usage", {})
        meta = {
            "model": data.get("model", DEFAULT_OPENAI_MODEL),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
        }
        return cards, meta


def debug_dump_cards(cards: Iterable[Card], *, path: Optional[Path] = None) -> None:
    """Optionally persist raw cards to aid debugging."""

    if path is not None:
        debug_path = Path(path)
    else:
        env_value = os.getenv("SR_DEBUG_DUMP")
        if not env_value:
            return
        debug_path = Path(env_value).expanduser()

    if debug_path.exists() and debug_path.is_dir():
        debug_path = debug_path / "cards.json"

    payload = [asdict(card) for card in cards]
    debug_path.parent.mkdir(parents=True, exist_ok=True)
    debug_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
