"""Agent job orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from .agent_strategy import AgentArtifacts, AgentContext, AgentStrategy
from .github_client import GitHubAPI
from .models import AgentJobPayload, AgentJobResult


@dataclass(slots=True)
class RepositoryContext:
    """Minimal pull request metadata required by the runner."""

    repo: str
    pr_number: int
    head_ref: str
    head_sha: str
    base_ref: str
    files: list[dict[str, Any]]


class AgentRunner:
    """Coordinates GitHub interactions with documentation generation."""

    def __init__(self, strategy: AgentStrategy) -> None:
        self._strategy = strategy

    async def _gather_context(
        self, github: GitHubAPI, job: AgentJobPayload
    ) -> RepositoryContext:
        pr = await github.get_pull_request(job.repository, job.pr_number)
        files = await github.get_pull_request_files(job.repository, job.pr_number)
        return RepositoryContext(
            repo=job.repository,
            pr_number=job.pr_number,
            head_ref=pr["head"]["ref"],
            head_sha=pr["head"]["sha"],
            base_ref=pr["base"]["ref"],
            files=files,
        )

    def _build_agent_context(
        self, repository: RepositoryContext, job: AgentJobPayload
    ) -> AgentContext:
        return AgentContext(
            repo=repository.repo,
            pr_number=repository.pr_number,
            head_ref=repository.head_ref,
            head_sha=repository.head_sha,
            base_ref=repository.base_ref,
            files=repository.files,
            mode=job.mode,
            notes=job.notes,
        )

    async def _apply_changes(
        self,
        github: GitHubAPI,
        repository: RepositoryContext,
        job: AgentJobPayload,
        artifacts: AgentArtifacts,
    ) -> AgentJobResult:
        if not artifacts.patches:
            return AgentJobResult(branch="", companion_pr_url=None, changed_files=[])
        branch = job.branch_name(repository.head_ref)
        await github.ensure_branch(repository.repo, branch, repository.head_sha)
        commit_message = artifacts.commit_message or f"auto-docs: {job.mode.value}"
        await github.upsert_files(
            repository.repo,
            branch,
            message=commit_message,
            files=(
                (patch.path.as_posix(), patch.content) for patch in artifacts.patches
            ),
        )
        pr = await github.create_pull_request(
            repository.repo,
            head=branch,
            base=repository.base_ref,
            title=artifacts.pr_title,
            body=artifacts.pr_body,
        )
        return AgentJobResult(
            branch=branch,
            companion_pr_url=cast(str | None, pr.get("html_url")),
            changed_files=[patch.path for patch in artifacts.patches],
        )

    async def run(self, github: GitHubAPI, job: AgentJobPayload) -> AgentJobResult:
        repository = await self._gather_context(github, job)
        context = self._build_agent_context(repository, job)
        artifacts = await self._strategy.generate(context)
        return await self._apply_changes(github, repository, job, artifacts)


__all__ = ["AgentRunner", "RepositoryContext"]
