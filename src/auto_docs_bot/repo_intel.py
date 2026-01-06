"""Light-weight helpers for collecting repository insights."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .commands import DocsMode


@dataclass(slots=True)
class RepoInsights:
    """Summarised information derived from PR metadata."""

    repo_hints: str
    diff_snippets: list[str]
    findings: list[str]


class RepoIntelBuilder:
    """Utility for generating :class:`RepoInsights` without cloning the repo."""

    def __init__(self, repo: str, pr_number: int, files: Iterable[dict[str, Any]]):
        self.repo = repo
        self.pr_number = pr_number
        self.files = list(files)

    def build(self) -> RepoInsights:
        doc_files: list[str] = []
        code_files: list[str] = []
        snippets: list[str] = []
        findings: list[str] = []
        for file in self.files:
            filename = file.get("filename", "")
            status = file.get("status", "modified")
            patch = file.get("patch")
            if filename.endswith((".md", ".mdx")):
                doc_files.append(filename)
            else:
                code_files.append(filename)
            if patch:
                snippets.append(f"[{filename} - {status}]\n{patch}")
            if status == "renamed":
                findings.append(
                    f"File {filename} was renamed; ensure references are updated in docs."
                )
        if not doc_files:
            findings.append(
                "No documentation files were part of the PR; agent should discover the"
                " appropriate targets based on repository search."
            )
        repo_hint_lines = [
            f"Repository: {self.repo}",
            f"Pull Request: #{self.pr_number}",
            f"Code files touched ({len(code_files)}): {', '.join(code_files) or 'none'}",
            f"Doc files touched ({len(doc_files)}): {', '.join(doc_files) or 'none'}",
        ]
        return RepoInsights(
            repo_hints="\n".join(repo_hint_lines),
            diff_snippets=snippets,
            findings=findings,
        )

    @staticmethod
    def payload_for_mode(mode: DocsMode, insights: RepoInsights, notes: str) -> dict[str, Any]:
        base_payload = {"notes": notes}
        if mode is DocsMode.QUICKSTART:
            return {**base_payload, "repo_hints": insights.repo_hints}
        if mode is DocsMode.UPDATE:
            return {**base_payload, "diff_snippets": insights.diff_snippets}
        return {**base_payload, "findings": insights.findings or insights.diff_snippets}


__all__ = ["RepoInsights", "RepoIntelBuilder"]
