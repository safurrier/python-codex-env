from __future__ import annotations

import random
import time
from collections.abc import Callable
from typing import Any

import requests


class DiscordAPIError(RuntimeError):
    pass


class DiscordClient:
    def __init__(
        self,
        token: str,
        base_url: str = "https://discord.com/api/v10",
        max_retries: int = 4,
        timeout: int = 20,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.timeout = timeout
        self.sleep_fn = sleep_fn or time.sleep
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bot {token}",
                "User-Agent": "dread/0.1 (+https://github.com)",
            }
        )

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        allow_202_retry: bool = False,
    ) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        backoff = 0.5
        for attempt in range(self.max_retries + 1):
            resp = self.session.request(
                method,
                url,
                params=params,
                json=json,
                timeout=self.timeout,
            )
            if resp.status_code == 202 and allow_202_retry:
                body = resp.json() if resp.content else {}
                delay = float(body.get("retry_after", 1.0))
                self.sleep_fn(delay)
                continue
            if resp.status_code == 429:
                delay = float(resp.headers.get("Retry-After", "1"))
                self.sleep_fn(delay)
                continue
            if resp.status_code >= 500 and attempt < self.max_retries:
                jitter = random.SystemRandom().uniform(0.0, 0.2)
                self.sleep_fn(backoff + jitter)
                backoff *= 2
                continue
            if resp.status_code >= 400:
                raise DiscordAPIError(f"{resp.status_code} {resp.text}")
            if resp.content:
                return resp.json()
            return None
        raise DiscordAPIError("Request retries exhausted")

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        allow_202_retry: bool = False,
    ) -> Any:
        return self.request("GET", path, params=params, allow_202_retry=allow_202_retry)

    def post(self, path: str, json: dict[str, Any]) -> Any:
        return self.request("POST", path, json=json)

    def put(self, path: str) -> Any:
        return self.request("PUT", path)

    def delete(self, path: str) -> Any:
        return self.request("DELETE", path)
