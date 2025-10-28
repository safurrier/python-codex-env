"""FastAPI application factory for the auto-docs bot."""

from __future__ import annotations

import logging
from typing import Callable

from fastapi import BackgroundTasks, FastAPI, Request

from .agent_runner import AgentRunner
from .agent_strategy import ClaudeCodeAgentStrategy, CodexCliAgentStrategy
from .baml_integration import build_doc_authoring_service
from .github_app import GitHubApp
from .github_client import GitHubAPI
from .settings import Settings
from .webhook import WebhookHandler

LOGGER = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    agent_runner: AgentRunner | None = None,
    github_app: GitHubApp | None = None,
    github_client_factory: Callable[[int], GitHubAPI] | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = settings or Settings.from_env()
    if github_app is None:
        if settings.github_app_id is None or settings.github_private_key is None:
            raise RuntimeError(
                "GITHUB_APP_ID and GITHUB_PRIVATE_KEY must be configured to start the app"
            )
        github_app = GitHubApp(
            app_id=int(settings.github_app_id),
            private_key=settings.github_private_key,
            base_url=settings.github_api_url,
        )
    if agent_runner is None:
        strategy: ClaudeCodeAgentStrategy | CodexCliAgentStrategy
        if settings.agent_backend == "claude":
            LOGGER.info("Initialising ClaudeCodeAgentStrategy via BAML client")
            doc_service = build_doc_authoring_service()
            strategy = ClaudeCodeAgentStrategy(doc_service)
        elif settings.agent_backend == "codex":
            executable = settings.codex_cli_path or "codex"
            LOGGER.info(
                "Initialising CodexCliAgentStrategy using executable %s", executable
            )
            strategy = CodexCliAgentStrategy(executable=executable)
        else:
            raise RuntimeError(
                "Unsupported AUTO_DOCS_AGENT_BACKEND. Expected 'claude' or 'codex'."
            )
        agent_runner = AgentRunner(strategy)
    handler = WebhookHandler(
        settings=settings,
        github_app=github_app,
        agent_runner=agent_runner,
        github_client_factory=github_client_factory,
    )

    app = FastAPI(title="Auto Docs Bot")

    @app.post("/github/webhook")  # type: ignore[misc]
    async def github_webhook(
        request: Request, background: BackgroundTasks
    ) -> dict[str, str]:
        return await handler.handle(request, background)

    @app.get("/healthz")  # type: ignore[misc]
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


__all__ = ["create_app"]
