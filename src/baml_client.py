"""Placeholder BAML client module."""

from __future__ import annotations

from typing import Any


def write_quickstart(
    payload: dict[str, Any],
) -> dict[str, Any]:  # pragma: no cover - placeholder
    raise RuntimeError(
        "BAML client not generated. Run `baml generate` to create write_quickstart()."
    )


def update_from_diff(
    payload: dict[str, Any],
) -> dict[str, Any]:  # pragma: no cover - placeholder
    raise RuntimeError(
        "BAML client not generated. Run `baml generate` to create update_from_diff()."
    )


def deep_update(
    payload: dict[str, Any],
) -> dict[str, Any]:  # pragma: no cover - placeholder
    raise RuntimeError(
        "BAML client not generated. Run `baml generate` to create deep_update()."
    )


__all__ = ["deep_update", "update_from_diff", "write_quickstart"]
