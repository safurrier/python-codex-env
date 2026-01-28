"""Configuration loading for Pi Docs Bot."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import PiDocsConfig, Scope, to_tuple


def load_config(path: Path | None = None) -> PiDocsConfig:
    """Load .pi-docs.yaml configuration if it exists."""

    config_path = path or Path(".pi-docs.yaml")
    if not config_path.exists():
        return PiDocsConfig()

    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    if not isinstance(raw, dict):
        return PiDocsConfig()

    return PiDocsConfig(
        allowed_paths=_read_list(raw.get("allowed_paths")),
        doc_build_command=_read_str(raw.get("doc_build_command")),
        doc_lint_command=_read_str(raw.get("doc_lint_command")),
        default_scope=_read_scope(raw.get("default_scope")),
        max_files=_read_int(raw.get("max_files"), fallback=PiDocsConfig().max_files),
        max_diff_lines=_read_int(
            raw.get("max_diff_lines"), fallback=PiDocsConfig().max_diff_lines
        ),
        deny_patterns=_read_list(raw.get("deny_patterns")) or (),
    )


def _read_list(value: Any) -> tuple[str, ...] | None:
    if value is None:
        return None
    if isinstance(value, list):
        items = [str(item) for item in value if str(item).strip()]
        return tuple(items) if items else None
    if isinstance(value, str):
        cleaned = value.strip()
        return (cleaned,) if cleaned else None
    return None


def _read_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _read_int(value: Any, fallback: int) -> int:
    if isinstance(value, int) and value > 0:
        return value
    return fallback


def _read_scope(value: Any) -> Scope:
    if isinstance(value, str):
        normalized = value.strip().lower()
        try:
            return Scope(normalized)
        except ValueError:
            return PiDocsConfig().default_scope
    return PiDocsConfig().default_scope


def merge_paths(*values: tuple[str, ...] | None) -> tuple[str, ...] | None:
    """Merge path lists in order, skipping None."""

    items: list[str] = []
    for entry in values:
        if entry:
            items.extend(entry)
    return to_tuple(items) if items else None
