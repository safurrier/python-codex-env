"""Unit tests for the auto-docs bot modules."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from auto_docs_bot import DocsCommand, DocsMode
from auto_docs_bot.agent_runner import AgentContext, AgentRunner
from auto_docs_bot.agent_strategies import AgentOutput, CodexCliAgentStrategy
from auto_docs_bot.models import AgentJobPayload, AgentJobResult, DocPatch, validate_patches
from auto_docs_bot.repo_intel import RepoIntelBuilder, RepoInsights
from auto_docs_bot.settings import Settings
from auto_docs_bot.webhook import WebhookHandler


class DummyGitHubApp:
    async def get_installation_token(self, installation_id: int) -> str:  # pragma: no cover
        return "token"


class FakeGitHubAPI:
    def __init__(self) -> None:
        self.reactions: list[tuple[str, int, str]] = []
        self.comments: list[tuple[str, int, str]] = []
        self.pull_request = {
            "head": {"ref": "feature", "sha": "abc123"},
            "base": {"ref": "main"},
        }
        self.files = []

    async def add_reaction(self, repo: str, comment_id: int, content: str) -> None:
        self.reactions.append((repo, comment_id, content))

    async def post_comment(self, repo: str, issue_number: int, body: str) -> None:
        self.comments.append((repo, issue_number, body))

    async def get_pull_request(self, repo: str, number: int) -> dict:
        return self.pull_request

    async def get_pull_request_files(self, repo: str, number: int) -> list[dict]:
        return self.files

    async def ensure_branch(self, repo: str, branch: str, sha: str) -> None:
        pass

    async def upsert_files(self, repo: str, branch: str, message: str, files):
        self.commit_message = message
        self.last_commit = list(files)

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


def test_repo_intel_payload_modes() -> None:
    files = [
        {"filename": "src/app.py", "status": "modified", "patch": "@@"},
        {"filename": "docs/guide.md", "status": "modified", "patch": "@@"},
    ]
    insights = RepoIntelBuilder("acme/repo", 5, files).build()
    quick = RepoIntelBuilder.payload_for_mode(DocsMode.QUICKSTART, insights, "note")
    update = RepoIntelBuilder.payload_for_mode(DocsMode.UPDATE, insights, "note")
    deep = RepoIntelBuilder.payload_for_mode(DocsMode.DEEP_UPDATE, insights, "note")
    assert "repo_hints" in quick
    assert "diff_snippets" in update
    assert "findings" in deep


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


def test_issue_comment_triggers_job_and_comment() -> None:
    async def run() -> None:
        github = FakeGitHubAPI()
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


def test_issue_comment_no_changes_posts_noop() -> None:
    async def run() -> None:
        github = FakeGitHubAPI()
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


class StubStrategy:
    def __init__(self, output: AgentOutput) -> None:
        self.output = output
        self.calls: list = []

    async def generate(self, job, context, insights):
        self.calls.append((job, context, insights))
        return self.output


def test_agent_runner_uses_strategy_output() -> None:
    async def run() -> None:
        github = FakeGitHubAPI()
        github.files = [{"filename": "src/app.py", "status": "modified", "patch": "@@"}]
        job = AgentJobPayload(
            repository="acme/repo",
            pr_number=3,
            installation_id=1,
            comment_id=2,
            mode=DocsMode.UPDATE,
            notes="",
        )
        output = AgentOutput(
            patches=[DocPatch(path=Path("docs/guide.md"), content="New content")],
            pr_title="Custom title",
            pr_body="Custom body",
            commit_message="Custom commit",
        )
        strategy = StubStrategy(output)
        runner = AgentRunner(strategy)
        result = await runner.run(github, job)
        assert result.branch.startswith("auto-docs/feature-")
        assert github.commit_message == "Custom commit"
        assert ("docs/guide.md", "New content") in github.last_commit
        assert github.pr_body == "Custom body"
        assert strategy.calls

    asyncio.run(run())


def test_codex_cli_strategy_parses_output(monkeypatch) -> None:
    strategy = CodexCliAgentStrategy(cli_path="codex")
    expected_response = {
        "patches": [
            {"path": "docs/guide.md", "content": "content", "rationale": "auto"},
        ],
        "pr_title": "CLI Title",
        "pr_body": "CLI Body",
        "commit_message": "CLI Commit",
    }

    import json
    from types import SimpleNamespace

    def fake_run(cmd, input, text, capture_output, check):
        payload = json.loads(input)
        assert payload["mode"] == DocsMode.QUICKSTART.value
        return SimpleNamespace(stdout=json.dumps(expected_response))

    monkeypatch.setattr("subprocess.run", fake_run)

    job = AgentJobPayload(
        repository="acme/repo",
        pr_number=1,
        installation_id=1,
        comment_id=1,
        mode=DocsMode.QUICKSTART,
        notes="",
    )
    context = AgentContext(
        repo="acme/repo",
        pr_number=1,
        head_ref="feature",
        head_sha="abc123",
        base_ref="main",
        files=[],
    )
    insights = RepoInsights(repo_hints="", diff_snippets=[], findings=[])

    async def run() -> None:
        output = await strategy.generate(job, context, insights)
        assert output.pr_title == "CLI Title"
        assert output.commit_message == "CLI Commit"
        assert output.patches and output.patches[0].path.as_posix() == "docs/guide.md"

    asyncio.run(run())
