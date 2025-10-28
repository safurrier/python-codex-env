"""GitHub REST integration built on top of githubkit."""

from __future__ import annotations

import base64
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, cast

from githubkit import GitHub
from githubkit.exception import RequestFailed


def _split_repo(full_name: str) -> tuple[str, str]:
    if "/" not in full_name:
        raise ValueError(f"Invalid repository name: {full_name!r}")
    owner, repo = full_name.split("/", 1)
    return owner, repo


@dataclass(slots=True)
class GitHubAPI:
    """Thin convenience wrapper around githubkit's :class:`GitHub` client."""

    client: GitHub

    async def post_comment(self, repo: str, issue_number: int, body: str) -> None:
        owner, name = _split_repo(repo)
        await self.client.rest.issues.async_create_comment(
            owner, name, issue_number, body=body
        )

    async def add_reaction(self, repo: str, comment_id: int, content: str) -> None:
        owner, name = _split_repo(repo)
        await self.client.rest.reactions.async_create_for_issue_comment(
            owner, name, comment_id, content=content
        )

    async def get_pull_request(self, repo: str, number: int) -> dict[str, Any]:
        owner, name = _split_repo(repo)
        response = await self.client.rest.pulls.async_get(owner, name, number)
        return cast(dict[str, Any], response.parsed_data.model_dump(by_alias=True))

    async def get_pull_request_files(
        self, repo: str, number: int
    ) -> list[dict[str, Any]]:
        owner, name = _split_repo(repo)
        paginator = self.client.rest.paginate(
            self.client.rest.pulls.async_list_files,
            owner,
            name,
            number,
            per_page=100,
        )
        files: list[dict[str, Any]] = []
        async for entry in paginator:
            files.append(cast(dict[str, Any], entry.model_dump(by_alias=True)))
        return files

    async def create_branch(self, repo: str, branch: str, sha: str) -> None:
        owner, name = _split_repo(repo)
        await self.client.rest.git.async_create_ref(
            owner,
            name,
            ref=f"refs/heads/{branch}",
            sha=sha,
        )

    async def ensure_branch(self, repo: str, branch: str, sha: str) -> None:
        try:
            await self.create_branch(repo, branch, sha)
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
            sha = await self._get_existing_file_sha(repo, path, branch)
            encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
            await self.client.rest.repos.async_create_or_update_file_contents(
                owner,
                name,
                path,
                message=message,
                content=encoded,
                branch=branch,
                sha=sha,
            )

    async def _get_existing_file_sha(
        self, repo: str, path: str, branch: str
    ) -> str | None:
        owner, name = _split_repo(repo)
        try:
            response = await self.client.rest.repos.async_get_content(
                owner,
                name,
                path,
                ref=branch,
            )
        except RequestFailed as exc:
            if exc.response.status_code == 404:
                return None
            raise
        data = response.parsed_data
        sha = getattr(data, "sha", None)
        if isinstance(sha, str):
            return sha
        return None

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
        response = await self.client.rest.pulls.async_create(
            owner,
            name,
            title=title,
            head=head,
            base=base,
            body=body,
            draft=draft,
        )
        return cast(dict[str, Any], response.parsed_data.model_dump(by_alias=True))

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
        kwargs: dict[str, Any] = {"name": name, "head_sha": head_sha, "status": status}
        if conclusion is not None:
            kwargs["conclusion"] = conclusion
        if output is not None:
            kwargs["output"] = output
        response = await self.client.rest.checks.async_create(
            owner, repo_name, **kwargs
        )
        return cast(dict[str, Any], response.parsed_data.model_dump(by_alias=True))


__all__ = ["GitHubAPI"]
