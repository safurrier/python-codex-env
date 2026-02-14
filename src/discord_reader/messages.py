from __future__ import annotations

from discord_reader.client import DiscordClient
from discord_reader.models import Message


def list_messages(
    client: DiscordClient,
    channel_id: str,
    *,
    limit: int = 50,
    before: str | None = None,
    after: str | None = None,
) -> list[Message]:
    params: dict[str, str | int] = {"limit": limit}
    if before:
        params["before"] = before
    if after:
        params["after"] = after
    data = client.get(f"channels/{channel_id}/messages", params=params)
    return [Message.model_validate(item) for item in data]


def tail_messages(
    client: DiscordClient, channel_id: str, *, pages: int = 1, limit: int = 50
) -> list[Message]:
    all_messages: list[Message] = []
    before: str | None = None
    for _ in range(pages):
        page = list_messages(client, channel_id, limit=limit, before=before)
        if not page:
            break
        all_messages.extend(page)
        before = page[-1].id
    return all_messages


def send_message(client: DiscordClient, channel_id: str, *, text: str) -> Message:
    data = client.post(f"channels/{channel_id}/messages", json={"content": text})
    return Message.model_validate(data)


def reply_message(
    client: DiscordClient, channel_id: str, message_id: str, *, text: str
) -> Message:
    payload = {
        "content": text,
        "message_reference": {"message_id": message_id, "channel_id": channel_id},
    }
    data = client.post(f"channels/{channel_id}/messages", json=payload)
    return Message.model_validate(data)


def add_reaction(
    client: DiscordClient, channel_id: str, message_id: str, emoji: str
) -> None:
    client.put(f"channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me")
