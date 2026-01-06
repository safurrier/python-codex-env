"""Pluggable strategies for running documentation agents."""

from __future__ import annotations

import asyncio
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from .baml_integration import DocAuthoringService
from .models import DocPatch, validate_patches
from .repo_intel import RepoInsights, RepoIntelBuilder

if TYPE_CHECKING:  # pragma: no cover - typing helpers
    from .agent_runner import AgentContext
    from .models import AgentJobPayload


@dataclass(slots=True)
class AgentOutput:
    """Outcome returned by a concrete agent strategy."""

    patches: list[DocPatch]
    pr_title: str | None = None
    pr_body: str | None = None
    commit_message: str | None = None


class AgentStrategy(Protocol):
    """Protocol implemented by documentation agent integrations."""

    async def generate(
        self,
        job: AgentJobPayload,
        context: AgentContext,
        insights: RepoInsights,
    ) -> AgentOutput:  # pragma: no cover - interface
        ...


@dataclass(slots=True)
class ClaudeCodeAgentStrategy:
    """Strategy that relies on Claude Code via the BAML authoring service."""

    authoring_service: DocAuthoringService

    async def generate(
        self,
        job: AgentJobPayload,
        context: AgentContext,
        insights: RepoInsights,
    ) -> AgentOutput:
        payload = RepoIntelBuilder.payload_for_mode(job.mode, insights, job.notes)
        patches = await asyncio.to_thread(
            self.authoring_service.generate_patches, job.mode, payload
        )
        if not patches:
            return AgentOutput(patches=[])
        summary_lines = ["## Summary"]
        for patch in patches:
            summary_lines.append(f"- {patch.path.as_posix()}")
        summary_lines.extend(
            [
                "",
                "## Context",
                f"Mode: {job.mode.value}",
            ]
        )
        if job.notes:
            summary_lines.append(f"Notes: {job.notes}")
        summary_lines.append("")
        summary_lines.append(f"Linked to #{context.pr_number}")
        return AgentOutput(
            patches=patches,
            pr_title=f"[auto-docs] {job.mode.value} for #{context.pr_number}",
            pr_body="\n".join(summary_lines),
            commit_message=f"auto-docs: {job.mode.value}",
        )


@dataclass(slots=True)
class CodexCliAgentStrategy:
    """Strategy that shells out to the Codex CLI in headless mode."""

    cli_path: str = "codex"
    args: tuple[str, ...] = ()

    async def generate(
        self,
        job: AgentJobPayload,
        context: AgentContext,
        insights: RepoInsights,
    ) -> AgentOutput:
        payload = {
            "mode": job.mode.value,
            "notes": job.notes,
            "context": {
                "repo": context.repo,
                "pr_number": context.pr_number,
                "head_ref": context.head_ref,
                "base_ref": context.base_ref,
            },
            "insights": {
                "repo_hints": insights.repo_hints,
                "diff_snippets": insights.diff_snippets,
                "findings": insights.findings,
            },
        }

        def _run_cli() -> subprocess.CompletedProcess[str]:
            return subprocess.run(  # noqa: S603 - command configurable at runtime
                (self.cli_path, *self.args),
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                check=True,
            )

        try:
            completed = await asyncio.to_thread(_run_cli)
        except subprocess.CalledProcessError as exc:  # pragma: no cover - defensive guard
            raise RuntimeError("Codex CLI execution failed") from exc

        stdout = (completed.stdout or "").strip()
        if not stdout:
            return AgentOutput(patches=[])

        try:
            response = json.loads(stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover - invalid CLI output
            raise RuntimeError("Codex CLI returned invalid JSON") from exc

        patches_payload = response.get("patches", [])
        patches = validate_patches(
            DocPatch(path=Path(raw["path"]), content=raw["content"], rationale=raw.get("rationale"))
            for raw in patches_payload
        )
        return AgentOutput(
            patches=patches,
            pr_title=response.get("pr_title"),
            pr_body=response.get("pr_body"),
            commit_message=response.get("commit_message"),
        )


__all__ = [
    "AgentOutput",
    "AgentStrategy",
    "ClaudeCodeAgentStrategy",
    "CodexCliAgentStrategy",
]
