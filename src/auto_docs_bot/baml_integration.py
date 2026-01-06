"""BAML integration helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from .commands import DocsMode
from .models import DocPatch, validate_patches


class _BamlCallable(Protocol):
    def __call__(self, payload: dict[str, Any]) -> Any:  # pragma: no cover - interface
        ...


@dataclass(slots=True)
class BamlResultAdapter:
    """Coerce BAML outputs into :class:`DocPatch` instances."""

    path_key: str = "path"
    content_key: str = "newContent"
    rationale_key: str = "rationale"

    def adapt(self, payload: Any) -> list[DocPatch]:
        patches = []
        for raw in payload or []:
            path_value = raw[self.path_key]
            content = raw[self.content_key]
            rationale = raw.get(self.rationale_key)
            patches.append(
                DocPatch(path=Path(path_value), content=content, rationale=rationale)
            )
        return validate_patches(patches)


@dataclass(slots=True)
class DocAuthoringService:
    """High-level orchestrator for BAML powered documentation updates."""

    write_quickstart: _BamlCallable | None
    update_from_diff: _BamlCallable | None
    deep_update: _BamlCallable | None
    adapter: BamlResultAdapter = field(default_factory=BamlResultAdapter)

    def ensure_available(self) -> None:
        if not (self.write_quickstart and self.update_from_diff and self.deep_update):
            raise RuntimeError(
                "BAML client functions are not available. Ensure the generated client is "
                "importable and that the environment has been bootstrapped."
            )

    def generate_patches(self, mode: DocsMode, payload: dict[str, Any]) -> list[DocPatch]:
        self.ensure_available()
        if mode is DocsMode.QUICKSTART:
            raw = self.write_quickstart(payload)
        elif mode is DocsMode.UPDATE:
            raw = self.update_from_diff(payload)
        else:
            raw = self.deep_update(payload)
        patches_payload = raw.get("patches") if isinstance(raw, dict) else raw
        return self.adapter.adapt(patches_payload)


def build_doc_authoring_service() -> DocAuthoringService:
    try:
        from baml_client import deep_update, update_from_diff, write_quickstart
    except Exception as exc:  # pragma: no cover - actual runtime requirement
        raise RuntimeError(
            "Unable to import generated BAML client. "
            "Run `baml generate` to produce the client before starting the service."
        ) from exc
    return DocAuthoringService(
        write_quickstart=write_quickstart,
        update_from_diff=update_from_diff,
        deep_update=deep_update,
    )


__all__ = ["BamlResultAdapter", "DocAuthoringService", "build_doc_authoring_service"]
