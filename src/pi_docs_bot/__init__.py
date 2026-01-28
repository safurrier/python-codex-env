"""Core primitives for the Pi Docs Bot workflow."""

from .command import ParseResult, parse_comment
from .config import PiDocsConfig, load_config
from .policy import (
    EffectiveSettings,
    PolicyCheckResult,
    allowed_paths_for_scope,
    check_diff_limits,
    check_path_policy,
    resolve_settings,
)
from .validation import DocSystemInfo, ValidationPlan, detect_doc_systems

__all__ = [
    "DocSystemInfo",
    "EffectiveSettings",
    "ParseResult",
    "PiDocsConfig",
    "PolicyCheckResult",
    "ValidationPlan",
    "allowed_paths_for_scope",
    "check_diff_limits",
    "check_path_policy",
    "detect_doc_systems",
    "load_config",
    "parse_comment",
    "resolve_settings",
]
