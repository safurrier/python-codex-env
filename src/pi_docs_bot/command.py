"""Parsing logic for PR comment commands."""

from __future__ import annotations

import re
import shlex

from .models import CommentCommand, Mode, ParseResult, Scope

COMMAND_PATTERN = re.compile(r"^\s*/pi\s+docs(?:\s+(?P<args>.*))?$", re.IGNORECASE)


def parse_comment(comment_body: str) -> ParseResult:
    """Parse a PR comment for a /pi docs command."""

    match = COMMAND_PATTERN.match(comment_body.strip())
    if not match:
        return ParseResult(command=None)

    args_text = match.group("args") or ""
    tokens = shlex.split(args_text)
    errors: list[str] = []
    options: dict[str, str] = {}
    free_text_parts: list[str] = []

    for token in tokens:
        if "=" in token:
            key, value = token.split("=", 1)
            options[key.strip().lower()] = value.strip()
        else:
            free_text_parts.append(token)

    scope = _parse_scope(options.get("scope"), errors)
    validate = _parse_bool(options.get("validate"), "validate", errors)
    mode = _parse_mode(options.get("mode"), errors)
    paths = _parse_paths(options.get("paths"))
    max_files = _parse_int(options.get("max_files"), "max_files", errors)
    max_diff_lines = _parse_int(options.get("max_diff_lines"), "max_diff_lines", errors)
    free_text = " ".join(free_text_parts).strip()

    if errors:
        return ParseResult(command=None, errors=tuple(errors))

    command = CommentCommand(
        scope=scope,
        validate=validate,
        mode=mode,
        paths=paths,
        max_files=max_files,
        max_diff_lines=max_diff_lines,
        free_text=free_text,
    )
    return ParseResult(command=command)


def _parse_scope(value: str | None, errors: list[str]) -> Scope | None:
    if value is None:
        return None
    normalized = value.lower()
    try:
        return Scope(normalized)
    except ValueError:
        errors.append(f"Invalid scope: {value}")
        return None


def _parse_mode(value: str | None, errors: list[str]) -> Mode | None:
    if value is None:
        return None
    normalized = value.lower()
    try:
        return Mode(normalized)
    except ValueError:
        errors.append(f"Invalid mode: {value}")
        return None


def _parse_bool(value: str | None, label: str, errors: list[str]) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    errors.append(f"Invalid {label}: {value}")
    return None


def _parse_int(value: str | None, label: str, errors: list[str]) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(value)
    except ValueError:
        errors.append(f"Invalid {label}: {value}")
        return None
    if parsed < 1:
        errors.append(f"{label} must be positive")
        return None
    return parsed


def _parse_paths(value: str | None) -> tuple[str, ...] | None:
    if value is None:
        return None
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if not parts:
        return None
    return tuple(parts)
