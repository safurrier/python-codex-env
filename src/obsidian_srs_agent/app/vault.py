"""Helpers for writing cards into an Obsidian vault."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from slugify import slugify

from .models import Card


class MarkdownVaultWriter:
    """Write generated cards into the expected folder structure."""

    def __init__(self, *, root: str) -> None:
        self._root = Path(root).expanduser().resolve()

    def write_cards(
        self,
        *,
        cards: List[Card],
        source_title: Optional[str],
        source_url: Optional[str],
        domain: str,
        topic: str,
        file_basename: Optional[str] = None,
    ) -> str:
        if not cards:
            raise ValueError("At least one card is required to write a deck.")
        if not self._root.exists():
            raise FileNotFoundError(
                f"Vault path '{self._root}' does not exist. Create it before running the agent."
            )

        deck_dir = self._root / "Decks" / slugify(domain) / slugify(topic)
        deck_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        base = file_basename or slugify(source_title or topic or "deck")
        filename = f"{timestamp}-{base}.md"
        file_path = deck_dir / filename

        frontmatter = {
            "title": source_title or base,
            "source_url": source_url or "",
            "created": datetime.now(timezone.utc).date().isoformat(),
            "sr_deck": True,
        }

        tag = f"#deck/{slugify(domain)}/{slugify(topic)}"
        lines = ["---"]
        for key, value in frontmatter.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{key}: {json.dumps(value)}")
            else:
                lines.append(f"{key}: {value}")
        lines.append("---\n")
        lines.append(tag)
        lines.append("\n")

        for card in cards:
            lines.append(card.render_line())

        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(file_path)
