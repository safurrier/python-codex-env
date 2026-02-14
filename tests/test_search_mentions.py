from __future__ import annotations

from datetime import datetime, timezone

import pytest

from discord_reader.client import DiscordAPIError
from discord_reader.models import Message
from discord_reader.search import search_mentions


class DummyClient:
    def __init__(self, responses: list[object]):
        self.responses = responses

    def get(self, *_args, **_kwargs):
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


def _msg(
    message_id: str, channel_id: str, content: str, mention_id: str | None = None
) -> dict:
    mentions = [] if mention_id is None else [{"id": mention_id, "username": "u"}]
    return {
        "id": message_id,
        "channel_id": channel_id,
        "author": {"id": "a1", "username": "author"},
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "content": content,
        "mentions": mentions,
        "attachments": [],
    }


def test_mentions_uses_search_path() -> None:
    client = DummyClient([{"messages": [[_msg("1", "10", "x", "42")]]}])
    hits = search_mentions(client, user_id="42", channel_id="10")
    assert len(hits) == 1
    assert hits[0].message.id == "1"


def test_mentions_fallback_when_search_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = DummyClient([DiscordAPIError("403 forbidden")])

    def fake_list_messages(_client, _channel_id, limit):
        del limit
        return [Message.model_validate(_msg("m1", "10", "hello <@42>"))]

    monkeypatch.setattr("discord_reader.search.list_messages", fake_list_messages)
    hits = search_mentions(client, user_id="42", channel_id="10")
    assert [h.message.id for h in hits] == ["m1"]


def test_mentions_requires_scope_for_fallback() -> None:
    client = DummyClient([DiscordAPIError("404")])
    with pytest.raises(DiscordAPIError):
        search_mentions(client, user_id="42")
