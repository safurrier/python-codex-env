"""Webhook handling logic for the auto-docs bot."""

from __future__ import annotations

import hmac
import json
import logging
from hashlib import sha256
from typing import Any, Callable

from fastapi import BackgroundTasks, HTTPException, Request

from .agent_runner import AgentRunner
from .commands import DocsCommand
from .github_app import GitHubApp
from .github_client import GitHubAPI
from .models import AgentJobPayload
from .settings import Settings

LOGGER = logging.getLogger(__name__)
DOCS_LABEL = "docs:auto"
EYES_REACTION = "eyes"
HOORAY_REACTION = "hooray"
CONFUSED_REACTION = "confused"


def verify_signature(secret: str | None, body: bytes, signature: str | None) -> None:
    if not secret:
        return
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature header")
    digest = hmac.new(secret.encode("utf-8"), body, sha256).hexdigest()
    expected = f"sha256={digest}"
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")


class WebhookHandler:
    """Handle incoming GitHub webhook payloads."""

    def __init__(
        self,
        settings: Settings,
        github_app: GitHubApp,
        agent_runner: AgentRunner,
        github_client_factory: Callable[[int], GitHubAPI] | None = None,
    ) -> None:
        self.settings = settings
        self.github_app = github_app
        self.agent_runner = agent_runner
        self.github_client_factory = github_client_factory or self._default_factory

    def _default_factory(self, installation_id: int) -> GitHubAPI:
        return self.github_app.installation_client(installation_id)

    async def handle(
        self, request: Request, background: BackgroundTasks
    ) -> dict[str, str]:
        body = await request.body()
        verify_signature(
            self.settings.github_webhook_secret,
            body,
            request.headers.get("X-Hub-Signature-256"),
        )
        event = request.headers.get("X-GitHub-Event")
        if not event:
            raise HTTPException(status_code=400, detail="Missing event header")
        payload = json.loads(body.decode("utf-8"))
        if event == "pull_request":
            await self._handle_pull_request(payload)
        elif event == "issue_comment":
            await self._handle_issue_comment(payload, background)
        else:
            LOGGER.debug("Ignoring unsupported event: %s", event)
        return {"status": "ok"}

    async def _handle_pull_request(self, payload: dict[str, Any]) -> None:
        if payload.get("action") != "labeled":
            return
        label = payload.get("label", {}).get("name")
        if label != DOCS_LABEL:
            return
        repo = payload["repository"]["full_name"]
        issue_number = payload["pull_request"]["number"]
        installation_id = payload.get("installation", {}).get("id")
        if installation_id is None:
            LOGGER.warning("No installation id on payload; cannot post helper comment")
            return
        github = self.github_client_factory(int(installation_id))
        helper_comment = (
            "Auto-docs is enabled for this PR.\n\n"
            "Run one of:\n"
            "  • /docs quickstart [notes]\n"
            "  • /docs update [notes]\n"
            "  • /docs deep-update [notes]"
        )
        await github.post_comment(repo, issue_number, helper_comment)

    async def _handle_issue_comment(
        self, payload: dict[str, Any], background: BackgroundTasks
    ) -> None:
        comment = payload.get("comment", {})
        body = comment.get("body", "")
        command = DocsCommand.parse(body)
        if not command:
            return
        issue = payload.get("issue", {})
        if "pull_request" not in issue:
            return
        labels = {label.get("name") for label in issue.get("labels", [])}
        if DOCS_LABEL not in labels:
            LOGGER.info("Ignoring command on PR without docs:auto label")
            return
        repo = payload["repository"]["full_name"]
        installation_id = payload.get("installation", {}).get("id")
        if installation_id is None:
            LOGGER.warning("Missing installation id; cannot run job")
            return
        github = self.github_client_factory(int(installation_id))
        comment_id = comment["id"]
        await github.add_reaction(repo, comment_id, EYES_REACTION)
        job = AgentJobPayload(
            repository=repo,
            pr_number=issue["number"],
            installation_id=int(installation_id),
            comment_id=comment_id,
            mode=command.mode,
            notes=command.notes,
        )

        async def runner() -> None:
            try:
                result = await self.agent_runner.run(github, job)
            except Exception as exc:  # pragma: no cover - defensive logging
                LOGGER.exception("Agent job failed: %%s", exc)
                await github.add_reaction(repo, comment_id, CONFUSED_REACTION)
                await github.post_comment(
                    repo,
                    job.pr_number,
                    "Auto-docs run failed. Please check the logs for details.",
                )
                return
            await github.add_reaction(repo, comment_id, HOORAY_REACTION)
            if not result.companion_pr_url:
                await github.post_comment(
                    repo,
                    job.pr_number,
                    "Auto-docs completed without documentation updates (no-op).",
                )
                return
            await github.post_comment(
                repo,
                job.pr_number,
                f"Auto-docs PR: {result.companion_pr_url}",
            )

        background.add_task(runner)


__all__ = ["WebhookHandler", "verify_signature"]
