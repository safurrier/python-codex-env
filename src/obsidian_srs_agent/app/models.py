"""Data models for the Obsidian SRS agent."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, List, Optional


@dataclass(slots=True)
class Card:
    """Represents a spaced-repetition card."""

    front: str
    back: str
    style: str = "basic"
    difficulty: str = "medium"
    tags: List[str] = field(default_factory=list)

    def render_line(self) -> str:
        """Render the card into the Obsidian SR plugin syntax."""

        if self.style == "reversed":
            separator = ":::"
        else:
            separator = "::"

        return f"{self.front}{separator}{self.back}".strip()


@dataclass(slots=True)
class CardGenControls:
    """Controls that steer generation of the cards."""

    num_cards: int = 10
    difficulty: Optional[str] = None
    focus_area: Optional[str] = None
    style: Optional[str] = None
    cloze_hint: Optional[str] = None


@dataclass(slots=True)
class SourceDoc:
    """Payload describing the source document used for generation."""

    text: str
    title: Optional[str] = None
    url: Optional[str] = None


@dataclass(slots=True)
class WriteResult:
    """Return type for vault write operations."""

    path: str
    created: date
    deck_tag: str


@dataclass(slots=True)
class GenerationResult:
    """Structured result returned by the generator step."""

    cards: List[Card]
    model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None

    def __post_init__(self) -> None:
        if any(card.front.strip() == "" or card.back.strip() == "" for card in self.cards):
            raise ValueError("Generated cards must have non-empty fronts and backs.")

    @property
    def count(self) -> int:
        return len(self.cards)


def ensure_card_styles(cards: Iterable[Card], style: Optional[str]) -> List[Card]:
    """Apply a fallback style to cards that do not declare one."""

    normalized_style = style or "basic"
    return [
        Card(
            front=card.front,
            back=card.back,
            style=card.style or normalized_style,
            difficulty=card.difficulty,
            tags=list(card.tags),
        )
        for card in cards
    ]
