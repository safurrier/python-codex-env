from __future__ import annotations

from typing import Any

from discord_reader.client import DiscordAPIError, DiscordClient


class FakeResponse:
    def __init__(
        self, status: int, payload: Any = None, headers: dict[str, str] | None = None
    ):
        self.status_code = status
        self._payload = payload
        self.headers = headers or {}
        self.text = "err"
        self.content = b"x" if payload is not None else b""

    def json(self) -> Any:
        return self._payload


class FakeSession:
    def __init__(self, responses: list[FakeResponse]):
        self.responses = responses
        self.headers: dict[str, str] = {}

    def request(self, *_: Any, **__: Any) -> FakeResponse:
        return self.responses.pop(0)


def test_retries_202_with_retry_after() -> None:
    sleeps: list[float] = []
    client = DiscordClient("t", sleep_fn=sleeps.append)
    client.session = FakeSession(
        [FakeResponse(202, {"retry_after": 0.25}), FakeResponse(200, {"ok": True})]
    )
    data = client.get("foo", allow_202_retry=True)
    assert data == {"ok": True}
    assert sleeps == [0.25]


def test_429_retry_then_success() -> None:
    sleeps: list[float] = []
    client = DiscordClient("t", sleep_fn=sleeps.append)
    client.session = FakeSession(
        [
            FakeResponse(429, headers={"Retry-After": "0.1"}),
            FakeResponse(200, {"ok": True}),
        ]
    )
    assert client.get("foo") == {"ok": True}
    assert sleeps == [0.1]


def test_raises_on_400() -> None:
    client = DiscordClient("t", sleep_fn=lambda _: None)
    client.session = FakeSession([FakeResponse(400, {"message": "bad"})])
    try:
        client.get("foo")
    except DiscordAPIError:
        pass
    else:
        raise AssertionError("expected DiscordAPIError")
