"""Unit tests for the auto-docs bot modules."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from auto_docs_bot import DocsCommand, DocsMode
from auto_docs_bot.agent_runner import AgentRunner
from auto_docs_bot.agent_strategy import (
    AgentArtifacts,
    AgentContext,
    CodexCliAgentStrategy,
)
from auto_docs_bot.models import AgentJobPayload, AgentJobResult, DocPatch, validate_patches
from auto_docs_bot.settings import Settings
from auto_docs_bot.webhook import WebhookHandler


class DummyGitHubApp:
    async def get_installation_token(self, installation_id: int) -> str:  # pragma: no cover
        return "token"


class FakeGitHubClient:
    def __init__(self) -> None:
        self.reactions: list[tuple[str, int, str]] = []
        self.comments: list[tuple[str, int, str]] = []
        self.pull_request = {
            "head": {"ref": "feature", "sha": "abc123"},
            "base": {"ref": "main"},
        }
        self.files = []
        self.branch_created: list[tuple[str, str, str]] = []

    async def add_reaction(self, repo: str, comment_id: int, content: str) -> None:
        self.reactions.append((repo, comment_id, content))

    async def post_comment(self, repo: str, issue_number: int, body: str) -> None:
        self.comments.append((repo, issue_number, body))

    async def get_pull_request(self, repo: str, number: int) -> dict:
        return self.pull_request

    async def get_pull_request_files(self, repo: str, number: int) -> list[dict]:
        return self.files

    async def ensure_branch(self, repo: str, branch: str, sha: str) -> None:
        self.branch_created.append((repo, branch, sha))

    async def upsert_files(self, repo: str, branch: str, message: str, files):
        self.last_commit = list(files)
        self.last_message = message

    async def create_pull_request(self, repo: str, head: str, base: str, title: str, body: str) -> dict:
        self.pr_body = body
        return {"html_url": "https://example.com/pr/2"}


class ImmediateTasks:
    def __init__(self) -> None:
        self._tasks: list = []

    def add_task(self, func, *args, **kwargs):
        async def runner():
            await func(*args, **kwargs)

        self._tasks.append(runner)

    async def run(self) -> None:
        for task in self._tasks:
            await task()


class StubAgentRunner:
    def __init__(self, result: AgentJobResult) -> None:
        self.result = result
        self.calls: list = []

    async def run(self, github, job):
        self.calls.append((github, job))
        return self.result


class StubAgentStrategy:
    def __init__(self, artifacts: AgentArtifacts) -> None:
        self.artifacts = artifacts
        self.calls: list[AgentContext] = []

    async def generate(self, context: AgentContext) -> AgentArtifacts:
        self.calls.append(context)
        return self.artifacts


@pytest.mark.parametrize(
    "command,expected",
    [
        ("/docs quickstart", DocsMode.QUICKSTART),
        ("/docs update some notes", DocsMode.UPDATE),
        ("/docs deep-update full sweep", DocsMode.DEEP_UPDATE),
    ],
)
def test_docs_command_parsing(command: str, expected: DocsMode) -> None:
    parsed = DocsCommand.parse(command)
    assert parsed is not None
    assert parsed.mode is expected


def test_validate_patches_allows_markdown() -> None:
    patches = [DocPatch(path=Path("docs/test.md"), content="")]
    validate_patches(patches)


@pytest.mark.parametrize(
    "filename,should_error",
    [("docs/file.md", False), ("src/main.py", True)],
)
def test_validate_patches_rejects_non_docs(filename: str, should_error: bool) -> None:
    patch = DocPatch(path=Path(filename), content="")
    if should_error:
        with pytest.raises(ValueError):
            validate_patches([patch])
    else:
        validate_patches([patch])


def test_branch_name_sanitises_refs() -> None:
    payload = AgentJobPayload(
        repository="acme/repo",
        pr_number=5,
        installation_id=1,
        comment_id=2,
        mode=DocsMode.UPDATE,
        notes="",
    )
    branch = payload.branch_name("feature/new-ui", timestamp=None)
    assert branch.startswith("auto-docs/feature-new-ui-")


def test_agent_runner_applies_strategy_artifacts() -> None:
    async def run() -> None:
        github = FakeGitHubClient()
        patches = [DocPatch(path=Path("docs/guide.md"), content="updated")]
        artifacts = AgentArtifacts(
            patches=patches,
            pr_title="[auto-docs] update for #3",
            pr_body="## Summary",
            commit_message="docs commit",
        )
        strategy = StubAgentStrategy(artifacts)
        runner = AgentRunner(strategy)
        job = AgentJobPayload(
            repository="acme/repo",
            pr_number=3,
            installation_id=1,
            comment_id=2,
            mode=DocsMode.UPDATE,
            notes="",
        )
        result = await runner.run(github, job)
        assert result.branch.startswith("auto-docs/")
        assert result.companion_pr_url == "https://example.com/pr/2"
        assert github.branch_created
        assert github.last_message == "docs commit"
        assert github.last_commit == [("docs/guide.md", "updated")]
        assert strategy.calls

    asyncio.run(run())


def test_issue_comment_triggers_job_and_comment() -> None:
    async def run() -> None:
        github = FakeGitHubClient()
        result = AgentJobResult(
            branch="auto-docs/feature-1",
            companion_pr_url="https://example.com/pr/2",
            changed_files=[Path("docs/guide.md")],
        )
        runner = StubAgentRunner(result)
        handler = WebhookHandler(
            settings=Settings(),
            github_app=DummyGitHubApp(),
            agent_runner=runner,
            github_api_factory=lambda token: github,
        )
        payload = {
            "comment": {"body": "/docs update add details", "id": 10},
            "issue": {"number": 3, "labels": [{"name": "docs:auto"}], "pull_request": {}},
            "repository": {"full_name": "acme/repo"},
            "installation": {"id": 5},
        }
        tasks = ImmediateTasks()
        await handler._handle_issue_comment(payload, tasks)
        assert ("acme/repo", 10, "eyes") in github.reactions
        await tasks.run()
        assert ("acme/repo", 10, "hooray") in github.reactions
        assert any("Auto-docs PR" in body for (_, _, body) in github.comments)
        assert runner.calls

    asyncio.run(run())


def test_codex_cli_agent_strategy_parses_output() -> None:
    async def run() -> None:
        def fake_run(payload: dict[str, Any]) -> str:
            assert payload["mode"] == DocsMode.UPDATE.value
            return json.dumps(
                {
                    "patches": [{"path": "docs/new.md", "content": "content"}],
                    "pr_title": "[auto-docs] custom",
                    "pr_body": "body",
                    "commit_message": "commit",
                }
            )

        strategy = CodexCliAgentStrategy(executable="codex", runner=fake_run)
        context = AgentContext(
            repo="acme/repo",
            pr_number=1,
            head_ref="feature",
            head_sha="abc",
            base_ref="main",
            files=[],
            mode=DocsMode.UPDATE,
            notes="",
        )
        artifacts = await strategy.generate(context)
        assert artifacts.pr_title == "[auto-docs] custom"
        assert artifacts.commit_message == "commit"
        assert artifacts.patches[0].path == Path("docs/new.md")

    asyncio.run(run())


def test_issue_comment_no_changes_posts_noop() -> None:
    async def run() -> None:
        github = FakeGitHubClient()
        result = AgentJobResult(branch="", companion_pr_url=None, changed_files=[])
        runner = StubAgentRunner(result)
        handler = WebhookHandler(
            settings=Settings(),
            github_app=DummyGitHubApp(),
            agent_runner=runner,
            github_api_factory=lambda token: github,
        )
        payload = {
            "comment": {"body": "/docs update", "id": 11},
            "issue": {"number": 4, "labels": [{"name": "docs:auto"}], "pull_request": {}},
            "repository": {"full_name": "acme/repo"},
            "installation": {"id": 5},
        }
        tasks = ImmediateTasks()
        await handler._handle_issue_comment(payload, tasks)
        await tasks.run()
        assert any("no-op" in body for (_, _, body) in github.comments)

    asyncio.run(run())
