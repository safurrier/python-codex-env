"""Environment-driven configuration for the auto-docs bot."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    """Configuration values sourced from environment variables."""

    github_app_id: int | None = None
    github_private_key: str | None = None
    github_webhook_secret: str | None = None
    github_api_url: str = "https://api.github.com"
    allowed_users: tuple[str, ...] = ()
    allowed_orgs: tuple[str, ...] = ()

    claude_api_key: str | None = None
    baml_environment: str | None = None
    sourcegraph_endpoint: str | None = None
    sourcegraph_token: str | None = None
    agent_backend: str = "claude"
    codex_cli_path: str | None = None

    def allow_all(self) -> bool:
        """Return ``True`` when no allow-list restrictions are configured."""

        return not self.allowed_orgs and not self.allowed_users

    @classmethod
    def from_env(cls) -> Settings:
        """Construct settings using process environment variables."""

        app_id = os.getenv("GITHUB_APP_ID")
        return cls(
            github_app_id=int(app_id) if app_id else None,
            github_private_key=os.getenv("GITHUB_PRIVATE_KEY"),
            github_webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET"),
            github_api_url=os.getenv("GITHUB_API_URL", "https://api.github.com"),
            allowed_users=_split_env_list("ALLOWED_USERS"),
            allowed_orgs=_split_env_list("ALLOWED_ORGS"),
            claude_api_key=os.getenv("CLAUDE_API_KEY"),
            baml_environment=os.getenv("BAML_ENV"),
            sourcegraph_endpoint=os.getenv("SOURCEGRAPH_ENDPOINT"),
            sourcegraph_token=os.getenv("SOURCEGRAPH_TOKEN"),
            agent_backend=os.getenv("AUTO_DOCS_AGENT_BACKEND", "claude").lower(),
            codex_cli_path=os.getenv("CODEX_CLI_PATH"),
        )


def _split_env_list(key: str) -> tuple[str, ...]:
    raw = os.getenv(key)
    if not raw:
        return ()
    return tuple(part.strip() for part in raw.split(",") if part.strip())


__all__ = ["Settings"]
