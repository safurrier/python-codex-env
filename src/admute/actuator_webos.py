"""Actuator for controlling LG webOS televisions over the local websocket API."""

from __future__ import annotations

import json
import ssl
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol, cast

from .actuator_base import ActuatorError, MuteActuator
from .state_machine import Transition, TransitionEvent


class WebSocketClientProtocol(Protocol):
    """Subset of the websocket API used by :class:`WebOSActuator`."""

    def send(self, message: str) -> None:  # pragma: no cover - interface only
        ...

    def recv(self) -> str:  # pragma: no cover - interface only
        ...

    def close(self) -> None:  # pragma: no cover - interface only
        ...


WebSocketFactory = Callable[[str, ssl.SSLContext], WebSocketClientProtocol]


class WebOSActuatorError(ActuatorError):
    """Raised when the actuator fails to communicate with the TV."""


@dataclass
class WebOSConfig:
    """Configuration parameters for the webOS actuator."""

    host: str
    client_key_path: Path | None = None
    secure: bool = True
    port: int = 3001


class WebOSActuator(MuteActuator):
    """Send mute/unmute commands to an LG webOS TV."""

    def __init__(
        self,
        config: WebOSConfig,
        *,
        websocket_factory: WebSocketFactory | None = None,
    ) -> None:
        self._config = config
        self._websocket_factory = websocket_factory or self._default_factory
        self._ws: WebSocketClientProtocol | None = None
        self._client_key: str | None = None
        self._message_id = 0

        if config.client_key_path and config.client_key_path.exists():
            self._client_key = config.client_key_path.read_text(encoding="utf8").strip()

    # -- Public API -------------------------------------------------
    def mute(self) -> None:
        self._ensure_connection()
        self._send_simple_request("ssap://audio/setMute", {"mute": True})

    def unmute(self) -> None:
        self._ensure_connection()
        self._send_simple_request("ssap://audio/setMute", {"mute": False})

    def close(self) -> None:
        if self._ws is not None:
            self._ws.close()
            self._ws = None

    # -- Internal helpers ------------------------------------------
    def _ensure_connection(self) -> None:
        if self._ws is None:
            self._connect()

    def _connect(self) -> None:
        uri = self._build_uri()
        context = ssl.create_default_context()
        if not self._config.secure:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        try:
            ws = self._websocket_factory(uri, context)
        except Exception as exc:  # pragma: no cover - trivial error passthrough
            raise WebOSActuatorError(f"Failed to connect to {uri}: {exc}") from exc
        self._ws = ws
        self._perform_registration()

    def _perform_registration(self) -> None:
        if self._ws is None:
            raise WebOSActuatorError("Websocket not connected")
        payload: dict[str, object] = {
            "type": "register",
            "id": self._next_message_id(),
            "payload": {
                "manifest": {
                    "manifestVersion": 1,
                    "permissions": ["LAUNCH", "CONTROL_INPUT_MEDIA_PLAYBACK"],
                    "localizedAppNames": {"": "AdMute", "en-US": "AdMute"},
                    "category": "admute",
                }
            },
        }
        payload_body = cast(dict[str, object], payload["payload"])
        if self._client_key:
            payload_body["client-key"] = self._client_key
        self._ws.send(json.dumps(payload))
        raw_response = self._ws.recv()
        response = json.loads(raw_response)
        if response.get("type") != "response":
            raise WebOSActuatorError(
                f"Unexpected registration response type: {response.get('type')}"
            )
        response_payload = cast(dict[str, Any], response.get("payload", {}))
        if not bool(response_payload.get("returnValue")):
            raise WebOSActuatorError("Registration was rejected by the TV")
        if not self._client_key:
            client_key = response_payload.get("client-key")
            if isinstance(client_key, str):
                self._client_key = client_key
                if self._config.client_key_path:
                    self._config.client_key_path.write_text(client_key, encoding="utf8")

    def _send_simple_request(self, uri: str, payload: dict[str, object]) -> None:
        if self._ws is None:
            raise WebOSActuatorError("Websocket not connected")
        message = {
            "type": "request",
            "id": self._next_message_id(),
            "uri": uri,
            "payload": payload,
        }
        self._ws.send(json.dumps(message))

    def _next_message_id(self) -> int:
        self._message_id += 1
        return self._message_id

    def _build_uri(self) -> str:
        scheme = "wss" if self._config.secure else "ws"
        return f"{scheme}://{self._config.host}:{self._config.port}/"

    @staticmethod
    def _default_factory(uri: str, context: ssl.SSLContext) -> WebSocketClientProtocol:
        try:
            from websocket import create_connection  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - requires optional dependency
            raise WebOSActuatorError(
                "websocket-client must be installed to use the default factory"
            ) from exc
        connection = create_connection(uri, sslopt={"context": context})
        return cast(WebSocketClientProtocol, connection)


def actuator_for_transition(transition: Transition) -> str | None:
    """Return a human readable description of a transition for logging."""

    if transition.event == TransitionEvent.AD_START:
        return "mute"
    if transition.event == TransitionEvent.CONTENT_START:
        return "unmute"
    if transition.force_unmute:
        return "force-unmute"
    return None
