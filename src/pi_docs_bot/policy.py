"""Policy enforcement for Pi Docs Bot changes."""

from __future__ import annotations

from dataclasses import replace
from fnmatch import fnmatch

from .models import (
    CommentCommand,
    EffectiveSettings,
    Mode,
    PiDocsConfig,
    PolicyCheckResult,
    Scope,
)


def allowed_paths_for_scope(scope: Scope) -> tuple[str, ...]:
    """Default allowed paths for a given scope."""

    if scope == Scope.ALL:
        return ("docs/**", "README.md", "CHANGELOG.md")
    if scope == Scope.README:
        return ("README.md",)
    if scope == Scope.CHANGELOG:
        return ("CHANGELOG.md",)
    return ("docs/**",)


def resolve_settings(
    command: CommentCommand, config: PiDocsConfig
) -> EffectiveSettings:
    """Resolve effective settings from command overrides and config."""

    scope = command.scope or config.default_scope
    validate = True if command.validate is None else command.validate
    mode = command.mode or Mode.STACKED
    max_files = command.max_files or config.max_files
    max_diff_lines = command.max_diff_lines or config.max_diff_lines

    if command.paths:
        allowed_paths = command.paths
    elif config.allowed_paths:
        allowed_paths = config.allowed_paths
    else:
        allowed_paths = allowed_paths_for_scope(scope)

    return EffectiveSettings(
        scope=scope,
        validate=validate,
        mode=mode,
        allowed_paths=allowed_paths,
        max_files=max_files,
        max_diff_lines=max_diff_lines,
        deny_patterns=config.deny_patterns,
        free_text=command.free_text,
    )


def check_path_policy(
    changed_paths: list[str],
    allowed_paths: tuple[str, ...],
    deny_patterns: tuple[str, ...] = (),
) -> PolicyCheckResult:
    """Ensure all changed paths are within allowed patterns."""

    violations: list[str] = []

    for path in changed_paths:
        normalized = path.replace("\\", "/")
        if _matches_any(normalized, deny_patterns):
            violations.append(f"Denied path: {path}")
            continue
        if not _matches_any(normalized, allowed_paths):
            violations.append(f"Not in allowlist: {path}")

    return PolicyCheckResult(allowed=not violations, violations=tuple(violations))


def check_diff_limits(
    changed_file_count: int,
    diff_line_count: int,
    max_files: int,
    max_diff_lines: int,
) -> PolicyCheckResult:
    """Check diff limits for file count and total line count."""

    violations: list[str] = []
    if changed_file_count > max_files:
        violations.append(
            f"Changed files ({changed_file_count}) exceed max_files ({max_files})"
        )
    if diff_line_count > max_diff_lines:
        violations.append(
            f"Diff lines ({diff_line_count}) exceed max_diff_lines ({max_diff_lines})"
        )
    return PolicyCheckResult(allowed=not violations, violations=tuple(violations))


def _matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    for pattern in patterns:
        normalized = pattern.replace("\\", "/")
        if fnmatch(path, normalized):
            return True
        if normalized.startswith("**/") and fnmatch(path, normalized[3:]):
            return True
    return False


def with_scope(settings: EffectiveSettings, scope: Scope) -> EffectiveSettings:
    """Return a new settings instance with updated scope."""

    updated = replace(settings, scope=scope)
    if settings.allowed_paths == allowed_paths_for_scope(settings.scope):
        return replace(updated, allowed_paths=allowed_paths_for_scope(scope))
    return updated
