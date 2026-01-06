"""GitHub REST API helpers for the auto-docs bot."""

from __future__ import annotations

import base64
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

try:  # pragma: no cover - runtime dependency injection
    import httpx
except ModuleNotFoundError:  # pragma: no cover - fallback for unit tests
    httpx = None  # type: ignore[assignment]


_GITHUB_ACCEPT_HEADER = "application/vnd.github+json"
_USER_AGENT = "auto-docs-bot/1.0"


@dataclass(slots=True)
class GitHubAPI:
    """Thin wrapper around GitHub's REST API."""

    token: str
    base_url: str = "https://api.github.com"
    client: Any = None

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": _GITHUB_ACCEPT_HEADER,
            "User-Agent": _USER_AGENT,
        }

    async def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        if httpx is None:  # pragma: no cover - runtime safeguard
            raise RuntimeError("httpx must be installed to interact with the GitHub API")

        close_client = False
        if self.client is None:
            client = httpx.AsyncClient(base_url=self.base_url)
            close_client = True
        else:
            client = self.client
        try:
            response = await client.request(
                method,
                url,
                headers={**self._headers(), **kwargs.pop("headers", {})},
                **kwargs,
            )
            response.raise_for_status()
            return response
        finally:
            if close_client:
                await client.aclose()

    async def post_comment(self, repo: str, issue_number: int, body: str) -> None:
        await self._request(
            "POST",
            f"/repos/{repo}/issues/{issue_number}/comments",
            json={"body": body},
        )

    async def add_reaction(self, repo: str, comment_id: int, content: str) -> None:
        await self._request(
            "POST",
            f"/repos/{repo}/issues/comments/{comment_id}/reactions",
            json={"content": content},
        )

    async def get_pull_request(self, repo: str, number: int) -> dict[str, Any]:
        response = await self._request("GET", f"/repos/{repo}/pulls/{number}")
        return response.json()

    async def get_pull_request_files(self, repo: str, number: int) -> list[dict[str, Any]]:
        response = await self._request("GET", f"/repos/{repo}/pulls/{number}/files")
        return response.json()

    async def create_branch(self, repo: str, branch: str, sha: str) -> None:
        await self._request(
            "POST",
            f"/repos/{repo}/git/refs",
            json={"ref": f"refs/heads/{branch}", "sha": sha},
        )

    async def ensure_branch(self, repo: str, branch: str, sha: str) -> None:
        if httpx is None:  # pragma: no cover - runtime safeguard
            raise RuntimeError("httpx must be installed to interact with the GitHub API")

        try:
            await self.create_branch(repo, branch, sha)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 422:
                # Branch already exists; ignore.
                return
            raise

    async def upsert_files(
        self,
        repo: str,
        branch: str,
        message: str,
        files: Iterable[tuple[str, str]],
    ) -> None:
        for path, content in files:
            sha = await self._get_existing_file_sha(repo, path, branch)
            payload = {
                "message": message,
                "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
                "branch": branch,
            }
            if sha:
                payload["sha"] = sha
            await self._request(
                "PUT",
                f"/repos/{repo}/contents/{path}",
                json=payload,
            )

    async def _get_existing_file_sha(self, repo: str, path: str, branch: str) -> str | None:
        if httpx is None:  # pragma: no cover - runtime safeguard
            raise RuntimeError("httpx must be installed to interact with the GitHub API")

        try:
            response = await self._request(
                "GET",
                f"/repos/{repo}/contents/{path}",
                params={"ref": branch},
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise
        data = response.json()
        return data.get("sha")

    async def create_pull_request(
        self,
        repo: str,
        head: str,
        base: str,
        title: str,
        body: str,
        draft: bool = False,
    ) -> dict[str, Any]:
        response = await self._request(
            "POST",
            f"/repos/{repo}/pulls",
            json={
                "title": title,
                "head": head,
                "base": base,
                "body": body,
                "draft": draft,
            },
        )
        return response.json()

    async def create_check_run(
        self,
        repo: str,
        name: str,
        head_sha: str,
        status: str,
        conclusion: str | None = None,
        output: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = await self._request(
            "POST",
            f"/repos/{repo}/check-runs",
            json={
                "name": name,
                "head_sha": head_sha,
                "status": status,
                "conclusion": conclusion,
                "output": output,
            },
            headers={"Accept": "application/vnd.github+json"},
        )
        return response.json()


__all__ = ["GitHubAPI"]
