"""Tests for the webOS actuator logic."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src.admute.actuator_webos import WebOSActuator, WebOSConfig


class FakeWebSocket:
    def __init__(self) -> None:
        self.sent: list[str] = []
        self.closed = False
        self._responses = [
            json.dumps({"type": "response", "payload": {"returnValue": True}})
        ]

    def send(self, message: str) -> None:
        self.sent.append(message)

    def recv(self) -> str:
        if not self._responses:
            raise RuntimeError("No more responses queued")
        return self._responses.pop(0)

    def close(self) -> None:
        self.closed = True


@pytest.fixture()
def fake_factory() -> tuple[FakeWebSocket, Any]:
    socket = FakeWebSocket()

    def _factory(uri: str, context: Any) -> FakeWebSocket:
        del uri, context
        return socket

    return socket, _factory


def test_webos_actuator_sends_mute_message(
    tmp_path: Path, fake_factory: tuple[FakeWebSocket, Any]
) -> None:
    socket, factory = fake_factory
    key_path = tmp_path / "client.key"
    key_path.write_text("existing", encoding="utf8")
    actuator = WebOSActuator(
        WebOSConfig(host="192.168.1.50", client_key_path=key_path, secure=False),
        websocket_factory=factory,
    )

    actuator.mute()

    assert len(socket.sent) >= 2
    register = json.loads(socket.sent[0])
    assert register["type"] == "register"
    mute = json.loads(socket.sent[-1])
    assert mute["uri"] == "ssap://audio/setMute"
    assert mute["payload"] == {"mute": True}


def test_webos_actuator_stores_new_client_key(
    tmp_path: Path, fake_factory: tuple[FakeWebSocket, Any]
) -> None:
    socket, factory = fake_factory
    socket._responses = [
        json.dumps(
            {
                "type": "response",
                "payload": {"returnValue": True, "client-key": "new-key"},
            }
        )
    ]
    key_path = tmp_path / "client.key"
    actuator = WebOSActuator(
        WebOSConfig(host="192.168.1.50", client_key_path=key_path, secure=False),
        websocket_factory=factory,
    )

    actuator.mute()

    assert key_path.read_text(encoding="utf8") == "new-key"
