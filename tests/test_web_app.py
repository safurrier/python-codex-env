"""Tests for the FastHtml-powered web control surface."""

from __future__ import annotations

import http.client
import time
from urllib.parse import urlparse

from src.admute.control import ActuatorController
from src.admute.web_app import WebAppConfig, WebAppServer


class DummyActuator:
    def __init__(self) -> None:
        self.commands: list[str] = []

    def mute(self) -> None:
        self.commands.append("mute")

    def unmute(self) -> None:
        self.commands.append("unmute")


def _post(url: str, data: str = "redirect=0") -> int:
    parsed = urlparse(url)
    body = data.encode("utf-8")
    connection = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=5)
    try:
        path = parsed.path or "/"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(body)),
        }
        connection.request("POST", path, body, headers)
        response = connection.getresponse()
        status = response.status
        response.read()
        return status
    finally:
        connection.close()


def test_web_app_serves_page_and_controls_actuator() -> None:
    actuator = DummyActuator()
    controller = ActuatorController(actuator)
    server = WebAppServer(controller, WebAppConfig(host="127.0.0.1", port=0, title="Test UI"))
    server.start()
    try:
        address = server.address
        assert address is not None
        base_url = f"http://{address[0]}:{address[1]}"

        # Give the server a moment to start listening.
        time.sleep(0.05)

        parsed = urlparse(base_url + "/")
        connection = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=5)
        try:
            connection.request("GET", parsed.path or "/")
            response = connection.getresponse()
            body = response.read().decode("utf-8")
        finally:
            connection.close()
        assert "Test UI" in body
        assert "Muted" in body or "Live" in body

        status = _post(base_url + "/mute")
        assert status in {204, 303}
        assert actuator.commands[-1] == "mute"
        assert controller.snapshot().muted is True

        status = _post(base_url + "/toggle")
        assert status in {204, 303}
        assert actuator.commands[-1] == "unmute"
        assert controller.snapshot().muted is False

        status = _post(base_url + "/unmute")
        assert status in {204, 303}
        assert actuator.commands[-1] == "unmute"
    finally:
        server.stop()

