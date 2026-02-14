from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from discord_reader.channels import get_channel, list_guild_channels
from discord_reader.guilds import get_guild, list_guilds
from discord_reader.messages import (
    add_reaction,
    list_messages,
    reply_message,
    send_message,
)


class SpyClient:
    def __init__(self) -> None:
        self.calls: list[
            tuple[str, str, dict[str, Any] | None, dict[str, Any] | None]
        ] = []

    def get(self, path: str, params: dict[str, Any] | None = None, **_: Any) -> Any:
        self.calls.append(("GET", path, params, None))
        if path.startswith("channels/") and path.endswith("/messages"):
            return [
                {
                    "id": "m1",
                    "channel_id": "10",
                    "author": {"id": "u1", "username": "a"},
                    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                    "content": "hello",
                    "mentions": [],
                    "attachments": [],
                }
            ]
        if path == "users/@me/guilds":
            return [{"id": "1", "name": "g"}]
        if path.startswith("guilds/") and path.endswith("/channels"):
            return [{"id": "10", "type": 0, "name": "general"}]
        if path.startswith("guilds/"):
            return {"id": "1", "name": "g"}
        if path.startswith("channels/"):
            return {"id": "10", "type": 0, "name": "general"}
        return {}

    def post(self, path: str, json: dict[str, Any]) -> Any:
        self.calls.append(("POST", path, None, json))
        return {
            "id": "m1",
            "channel_id": "10",
            "author": {"id": "u1", "username": "a"},
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "content": json["content"],
            "mentions": [],
            "attachments": [],
        }

    def put(self, path: str) -> Any:
        self.calls.append(("PUT", path, None, None))
        return None


def test_guild_routes() -> None:
    client = SpyClient()
    list_guilds(client)
    get_guild(client, "1")
    assert client.calls[0][:2] == ("GET", "users/@me/guilds")
    assert client.calls[1][:2] == ("GET", "guilds/1")


def test_channel_routes() -> None:
    client = SpyClient()
    list_guild_channels(client, "1")
    get_channel(client, "10")
    assert client.calls[0][:2] == ("GET", "guilds/1/channels")
    assert client.calls[1][:2] == ("GET", "channels/10")


def test_message_routes_and_params() -> None:
    client = SpyClient()
    list_messages(client, "10", limit=999, before="5")
    send_message(client, "10", text="hello")
    reply_message(client, "10", "5", text="reply")
    add_reaction(client, "10", "5", "%F0%9F%91%8D")

    assert client.calls[0] == (
        "GET",
        "channels/10/messages",
        {"limit": 100, "before": "5"},
        None,
    )
    assert client.calls[1] == (
        "POST",
        "channels/10/messages",
        None,
        {"content": "hello"},
    )
    assert client.calls[2][0:2] == ("POST", "channels/10/messages")
    assert client.calls[2][3] == {
        "content": "reply",
        "message_reference": {"message_id": "5", "channel_id": "10"},
    }
    assert client.calls[3] == (
        "PUT",
        "channels/10/messages/5/reactions/%F0%9F%91%8D/@me",
        None,
        None,
    )
