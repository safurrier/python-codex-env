"""Data models for the Pi Docs Bot workflow."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum


class Scope(str, Enum):
    """Documentation scope for updates."""

    DOCS = "docs"
    README = "readme"
    CHANGELOG = "changelog"
    ALL = "all"


class Mode(str, Enum):
    """How to deliver the docs changes."""

    STACKED = "stacked"
    COMMIT_TO_PR_BRANCH = "commit-to-pr-branch"


@dataclass(frozen=True)
class CommentCommand:
    """Parsed command options from a PR comment."""

    scope: Scope | None = None
    validate: bool | None = None
    mode: Mode | None = None
    paths: tuple[str, ...] | None = None
    max_files: int | None = None
    max_diff_lines: int | None = None
    free_text: str = ""


@dataclass(frozen=True)
class ParseResult:
    """Result of parsing a command comment."""

    command: CommentCommand | None
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class PiDocsConfig:
    """Repo-level configuration for Pi Docs Bot."""

    allowed_paths: tuple[str, ...] | None = None
    doc_build_command: str | None = None
    doc_lint_command: str | None = None
    default_scope: Scope = Scope.DOCS
    max_files: int = 50
    max_diff_lines: int = 2000
    deny_patterns: tuple[str, ...] = ()


@dataclass(frozen=True)
class EffectiveSettings:
    """Resolved settings after applying command overrides and config."""

    scope: Scope
    validate: bool
    mode: Mode
    allowed_paths: tuple[str, ...]
    max_files: int
    max_diff_lines: int
    deny_patterns: tuple[str, ...]
    free_text: str


@dataclass(frozen=True)
class PolicyCheckResult:
    """Result of enforcing policy constraints."""

    allowed: bool
    violations: tuple[str, ...]


@dataclass(frozen=True)
class ValidationPlan:
    """Validation commands to run for documentation."""

    build_command: str | None
    lint_command: str | None
    detected_systems: tuple[str, ...]


@dataclass(frozen=True)
class DocSystemInfo:
    """Detected documentation systems and context."""

    systems: tuple[str, ...]
    build_command: str | None
    lint_command: str | None
    notes: tuple[str, ...]


def to_tuple(values: Iterable[str] | None) -> tuple[str, ...] | None:
    """Normalize an iterable of strings into a tuple, if provided."""

    if values is None:
        return None
    return tuple(values)
