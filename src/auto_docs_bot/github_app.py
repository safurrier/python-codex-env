"""Helpers for working with GitHub App authentication."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

try:  # pragma: no cover - runtime dependency injection
    import httpx
except ModuleNotFoundError:  # pragma: no cover - fallback for unit tests
    httpx = None  # type: ignore[assignment]

try:  # pragma: no cover - runtime dependency injection
    import jwt
except ModuleNotFoundError:  # pragma: no cover - fallback for unit tests
    class _MissingJWTModule:
        @staticmethod
        def encode(*args, **kwargs):
            raise RuntimeError("PyJWT must be installed to use GitHubApp")

    jwt = _MissingJWTModule()  # type: ignore[assignment]


@dataclass(slots=True)
class GitHubApp:
    """Utility for exchanging installation tokens."""

    app_id: int
    private_key: str
    base_url: str = "https://api.github.com"
    client: Any = None

    def _jwt(self) -> str:
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + (9 * 60),
            "iss": self.app_id,
        }
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    async def get_installation_token(self, installation_id: int) -> str:
        if httpx is None:  # pragma: no cover - runtime safeguard
            raise RuntimeError("httpx must be installed to request installation tokens")

        close_client = False

        if self.client is None:
            client = httpx.AsyncClient(base_url=self.base_url)
            close_client = True
        else:
            client = self.client
        try:
            response = await client.post(
                f"/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {self._jwt()}",
                    "Accept": "application/vnd.github+json",
                },
            )
            response.raise_for_status()
            data = response.json()
            token = data.get("token")
            if not token:  # pragma: no cover - GitHub always returns token
                raise RuntimeError("GitHub response did not include an access token")
            return token
        finally:
            if close_client:
                await client.aclose()


__all__ = ["GitHubApp"]
