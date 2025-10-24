"""Auto-docs bot package."""

from __future__ import annotations

from .commands import DocsCommand, DocsMode
from .models import AgentJobPayload, DocPatch


def create_app(*args, **kwargs):  # type: ignore[override]
    """Lazy import for the FastAPI app factory."""

    from .app import create_app as _create_app

    return _create_app(*args, **kwargs)


__all__ = [
    "AgentJobPayload",
    "DocPatch",
    "DocsCommand",
    "DocsMode",
    "create_app",
]
