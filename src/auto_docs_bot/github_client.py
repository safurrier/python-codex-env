"""GitHub REST API helpers backed by githubkit."""

from __future__ import annotations

import base64
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, cast

from githubkit import GitHub
from githubkit.exception import RequestFailed

_USER_AGENT = "auto-docs-bot/1.0"


def _split_repo(repo: str) -> tuple[str, str]:
    if "/" not in repo:
        raise ValueError(f"Invalid repository identifier: {repo!r}")
    owner, name = repo.split("/", 1)
    return owner, name


@dataclass(slots=True)
class GitHubClient:
    """Thin wrapper around the GitHub REST API using githubkit."""

    token: str
    base_url: str = "https://api.github.com"
    _client: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._client = GitHub(
            auth=self.token, base_url=self.base_url, user_agent=_USER_AGENT
        )

    async def post_comment(self, repo: str, issue_number: int, body: str) -> None:
        owner, name = _split_repo(repo)
        await self._client.rest.issues.async_create_comment(
            owner=owner,
            repo=name,
            issue_number=issue_number,
            data={"body": body},
        )

    async def add_reaction(self, repo: str, comment_id: int, content: str) -> None:
        owner, name = _split_repo(repo)
        await self._client.rest.reactions.async_create_for_issue_comment(
            owner=owner,
            repo=name,
            comment_id=comment_id,
            data={"content": content},
        )

    async def get_pull_request(self, repo: str, number: int) -> dict[str, Any]:
        owner, name = _split_repo(repo)
        response = await self._client.rest.pulls.async_get(
            owner=owner, repo=name, pull_number=number
        )
        return cast(dict[str, Any], response.parsed_data.model_dump())

    async def get_pull_request_files(
        self, repo: str, number: int
    ) -> list[dict[str, Any]]:
        owner, name = _split_repo(repo)
        response = await self._client.rest.pulls.async_list_files(
            owner=owner, repo=name, pull_number=number
        )
        return [
            cast(dict[str, Any], item.model_dump()) for item in response.parsed_data
        ]

    async def ensure_branch(self, repo: str, branch: str, sha: str) -> None:
        owner, name = _split_repo(repo)
        try:
            await self._client.rest.git.async_create_ref(
                owner=owner,
                repo=name,
                data={"ref": f"refs/heads/{branch}", "sha": sha},
            )
        except RequestFailed as exc:
            if exc.response.status_code == 422:
                return
            raise

    async def upsert_files(
        self,
        repo: str,
        branch: str,
        message: str,
        files: Iterable[tuple[str, str]],
    ) -> None:
        owner, name = _split_repo(repo)
        for path, content in files:
            sha = await self._get_existing_file_sha(owner, name, path, branch)
            payload = {
                "message": message,
                "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
                "branch": branch,
            }
            if sha:
                payload["sha"] = sha
            await self._client.rest.repos.async_create_or_update_file_contents(
                owner=owner,
                repo=name,
                path=path,
                data=payload,
            )

    async def _get_existing_file_sha(
        self, owner: str, name: str, path: str, branch: str
    ) -> str | None:
        try:
            response = await self._client.rest.repos.async_get_content(
                owner=owner,
                repo=name,
                path=path,
                ref=branch,
            )
        except RequestFailed as exc:
            if exc.response.status_code == 404:
                return None
            raise
        data = response.parsed_data
        if isinstance(data, list):
            return None
        return cast(str | None, getattr(data, "sha", None))

    async def create_pull_request(
        self,
        repo: str,
        head: str,
        base: str,
        title: str,
        body: str,
        draft: bool = False,
    ) -> dict[str, Any]:
        owner, name = _split_repo(repo)
        response = await self._client.rest.pulls.async_create(
            owner=owner,
            repo=name,
            data={
                "title": title,
                "head": head,
                "base": base,
                "body": body,
                "draft": draft,
            },
        )
        return cast(dict[str, Any], response.parsed_data.model_dump())

    async def create_check_run(
        self,
        repo: str,
        name: str,
        head_sha: str,
        status: str,
        conclusion: str | None = None,
        output: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        owner, repo_name = _split_repo(repo)
        payload: dict[str, Any] = {
            "name": name,
            "head_sha": head_sha,
            "status": status,
        }
        if conclusion is not None:
            payload["conclusion"] = conclusion
        if output is not None:
            payload["output"] = output
        response = await self._client.rest.checks.async_create(
            owner=owner,
            repo=repo_name,
            data=payload,
        )
        return cast(dict[str, Any], response.parsed_data.model_dump())


__all__ = ["GitHubClient"]
