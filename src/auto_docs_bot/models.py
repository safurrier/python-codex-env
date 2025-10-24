"""Shared data models for the auto-docs bot."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .commands import DocsMode

_ALLOWED_DOC_EXTENSIONS = {".md", ".mdx"}


@dataclass(slots=True)
class DocPatch:
    """Representation of a documentation patch returned by BAML."""

    path: Path
    content: str
    rationale: str | None = None

    def ensure_valid(self) -> None:
        """Validate that the patch points to a supported documentation file."""

        suffix = self.path.suffix.lower()
        if suffix not in _ALLOWED_DOC_EXTENSIONS:
            raise ValueError(
                f"Unsupported documentation extension {suffix!r} for {self.path}"
            )


@dataclass(slots=True)
class AgentJobPayload:
    """Minimal metadata required to kick off an agent job."""

    repository: str
    pr_number: int
    installation_id: int
    comment_id: int
    mode: DocsMode
    notes: str

    def branch_name(self, head_ref: str, timestamp: datetime | None = None) -> str:
        """Generate a deterministic companion branch name."""

        ts = (timestamp or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S")
        sanitized = head_ref.replace("/", "-")
        return f"auto-docs/{sanitized}-{ts}"


@dataclass(slots=True)
class AgentJobResult:
    """Outcome of an agent job run."""

    branch: str
    companion_pr_url: str | None
    changed_files: Sequence[Path]


def validate_patches(patches: Iterable[DocPatch]) -> list[DocPatch]:
    """Validate and normalise a collection of :class:`DocPatch` objects."""

    validated: list[DocPatch] = []
    for patch in patches:
        patch.ensure_valid()
        validated.append(patch)
    return validated


__all__ = [
    "AgentJobPayload",
    "AgentJobResult",
    "DocPatch",
    "validate_patches",
]
