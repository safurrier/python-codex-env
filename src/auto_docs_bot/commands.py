"""Parsing utilities for slash commands."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

_COMMAND_PATTERN = re.compile(
    r"^/docs\s+(quickstart|update|deep-update)\b(?:\s+(?P<notes>.+))?\s*$",
    re.IGNORECASE,
)


class DocsMode(str, Enum):
    """Supported automation modes."""

    QUICKSTART = "quickstart"
    UPDATE = "update"
    DEEP_UPDATE = "deep-update"

    @classmethod
    def from_raw(cls, value: str) -> DocsMode:
        """Coerce an arbitrary string into a :class:`DocsMode`.

        The conversion is case-insensitive and accepts common aliases.
        """

        normalised = value.strip().lower()
        alias_map = {
            "qs": cls.QUICKSTART,
            "quick": cls.QUICKSTART,
            "quick-start": cls.QUICKSTART,
            "deep": cls.DEEP_UPDATE,
            "deepupdate": cls.DEEP_UPDATE,
            "deep_update": cls.DEEP_UPDATE,
        }
        if normalised in alias_map:
            return alias_map[normalised]
        try:
            return cls(normalised)
        except ValueError as exc:  # pragma: no cover - defensive branch
            raise ValueError(f"Unsupported docs mode: {value!r}") from exc


@dataclass(slots=True)
class DocsCommand:
    """Parsed representation of a ``/docs`` slash command."""

    mode: DocsMode
    notes: str

    @classmethod
    def parse(cls, text: str) -> DocsCommand | None:
        """Parse *text* into a :class:`DocsCommand`.

        Returns ``None`` when *text* does not match the expected pattern.
        The parser is case-insensitive and trims whitespace around the
        optional ``notes`` portion.
        """

        match = _COMMAND_PATTERN.match(text.strip())
        if match is None:
            return None
        raw_mode = match.group(1)
        notes = match.group("notes") or ""
        return cls(mode=DocsMode.from_raw(raw_mode), notes=notes.strip())


__all__ = ["DocsCommand", "DocsMode"]
