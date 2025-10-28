"""GitHub App helpers backed by githubkit."""

from __future__ import annotations

from dataclasses import dataclass

from githubkit import AppInstallationAuthStrategy, GitHub

from .github_client import GitHubAPI


@dataclass(slots=True)
class GitHubApp:
    """Factory for creating installation-scoped GitHub clients."""

    app_id: int
    private_key: str
    base_url: str = "https://api.github.com"

    def installation_client(self, installation_id: int) -> GitHubAPI:
        auth = AppInstallationAuthStrategy(
            app_id=self.app_id,
            private_key=self.private_key,
            installation_id=installation_id,
        )
        client = GitHub(auth=auth, base_url=self.base_url, follow_redirects=True)
        return GitHubAPI(client)


__all__ = ["GitHubApp"]
