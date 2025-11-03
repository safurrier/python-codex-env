"""Simple FastHtml-powered control surface for manual mute toggles."""

from __future__ import annotations

import logging
import threading
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable, SupportsInt, cast
from urllib.parse import parse_qs

from fast_html import body, button, div, form, h1, head, html, p, render, style, title

from .control import ActuatorController, ActuatorStatus

LOGGER = logging.getLogger(__name__)


@dataclass
class WebAppConfig:
    """Configuration for the FastHtml control server."""

    host: str = "127.0.0.1"
    port: int = 8765
    title: str = "AdMute Control"


def _format_timestamp(ts: datetime) -> str:
    return ts.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def _render_page(config: WebAppConfig, status: ActuatorStatus) -> str:
    """Render the HTML control panel."""

    badge_color = "#e74c3c" if status.muted else "#2ecc71"
    badge_text = "Muted" if status.muted else "Live"
    doc = html(
        [
            head(
                [
                    title(config.title),
                    style(
                        """
                        body { font-family: system-ui, sans-serif; margin: 2rem; }
                        .status { display: inline-block; padding: 0.5rem 1rem; border-radius: 999px; color: white; }
                        .actions { margin-top: 1.5rem; display: flex; gap: 1rem; }
                        button { font-size: 1rem; padding: 0.5rem 1.5rem; cursor: pointer; }
                        """
                    ),
                ]
            ),
            body(
                [
                    h1(config.title),
                    div(
                        [
                            div(
                                badge_text,
                                style=f"background-color: {badge_color};",
                                **{"class": "status"},
                            ),
                        ]
                    ),
                    p(f"Last action: {status.last_reason} ({status.origin})"),
                    p(f"Updated: {_format_timestamp(status.updated_at)}"),
                    p(f"Command count: {status.command_count}"),
                    div(
                        [
                            form(
                                button("Mute"),
                                method="post",
                                action="/mute",
                            ),
                            form(
                                button("Unmute"),
                                method="post",
                                action="/unmute",
                            ),
                            form(
                                button("Toggle"),
                                method="post",
                                action="/toggle",
                            ),
                        ],
                        **{"class": "actions"},
                    ),
                ]
            ),
        ]
    )
    return render(doc)


class _ControlRequestHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests for the control server."""

    controller: ActuatorController
    config: WebAppConfig

    def do_GET(self) -> None:
        status = self.controller.snapshot()
        page = _render_page(self.config, status)
        body_bytes = page.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(length)
        params = parse_qs(body_bytes.decode("utf-8"))
        action = self.path.lower()
        if action == "/mute":
            LOGGER.info("Manual mute requested via web UI")
            self.controller.mute(reason="manual", origin="web")
        elif action == "/unmute":
            LOGGER.info("Manual unmute requested via web UI")
            self.controller.unmute(reason="manual", origin="web")
        elif action == "/toggle":
            LOGGER.info("Manual toggle requested via web UI")
            self.controller.toggle(reason="manual", origin="web")
        else:
            LOGGER.warning("Unknown POST path: %s", self.path)
        if params.get("redirect", ["1"])[0] == "1":
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        LOGGER.debug("Control server: " + format, *args)


class WebAppServer:
    """Threaded HTTP server that exposes manual controls."""

    def __init__(self, controller: ActuatorController, config: WebAppConfig) -> None:
        self._controller = controller
        self._config = config
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def address(self) -> tuple[str, int] | None:
        if self._server is None:
            return None
        address = cast(Sequence[object], self._server.server_address)
        host = str(address[0])
        port = int(cast(SupportsInt, address[1]))
        return host, port

    def start(self) -> None:
        if self._server is not None:
            return

        controller = self._controller
        config = self._config

        class Handler(_ControlRequestHandler):
            pass

        Handler.controller = controller
        Handler.config = config

        server = ThreadingHTTPServer((config.host, config.port), Handler)
        self._server = server

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self._thread = thread
        LOGGER.info("Started FastHtml control server on %s:%s", *server.server_address)

    def stop(self) -> None:
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2)
        self._server = None
        self._thread = None


def build_web_app(
    controller: ActuatorController, config_factory: Callable[[], WebAppConfig]
) -> WebAppServer:
    """Construct and start a web control app."""

    app = WebAppServer(controller, config_factory())
    app.start()
    return app

