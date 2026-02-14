from __future__ import annotations

from datetime import datetime

from discord_reader.channels import list_guild_channels
from discord_reader.client import DiscordAPIError, DiscordClient
from discord_reader.messages import list_messages
from discord_reader.models import MentionHit, Message

SEARCH_UNAVAILABLE_CODES = ("403", "404", "405", "501")


def _is_mention(message: Message, user_id: str) -> bool:
    if any(user.id == user_id for user in message.mentions):
        return True
    return f"<@{user_id}>" in message.content or f"<@!{user_id}>" in message.content


def _parse_since(*, since: str | None) -> datetime | None:
    if not since:
        return None
    return datetime.fromisoformat(since.replace("Z", "+00:00"))


def search_mentions(
    client: DiscordClient,
    *,
    user_id: str,
    guild_id: str | None = None,
    channel_id: str | None = None,
    since: str | None = None,
    last: int | None = None,
    limit: int = 50,
) -> list[MentionHit]:
    since_dt = _parse_since(since=since)
    safe_limit = max(1, min(limit, 100))
    scan_limit = max(safe_limit, min(last or safe_limit, 500))

    scopes = [channel_id] if channel_id else []
    if guild_id and not scopes:
        scopes = [c.id for c in list_guild_channels(client, guild_id)]

    hits: list[MentionHit] = []
    search_path = None
    if channel_id:
        search_path = f"channels/{channel_id}/messages/search"
    elif guild_id:
        search_path = f"guilds/{guild_id}/messages/search"

    if search_path:
        try:
            search_data = client.get(
                search_path,
                params={"mentions": user_id, "limit": safe_limit},
                allow_202_retry=True,
            )
            for group in search_data.get("messages", []):
                for raw_msg in group:
                    msg = Message.model_validate(raw_msg)
                    if since_dt and msg.timestamp < since_dt:
                        continue
                    hits.append(MentionHit(channel_id=msg.channel_id, message=msg))
            return hits[:safe_limit]
        except DiscordAPIError as exc:
            if not any(code in str(exc) for code in SEARCH_UNAVAILABLE_CODES):
                raise

    if not scopes:
        raise DiscordAPIError(
            "Mentions fallback requires --guild or --channel scope when search is unavailable"
        )

    for scope_channel_id in scopes:
        for msg in list_messages(client, scope_channel_id, limit=scan_limit):
            if since_dt and msg.timestamp < since_dt:
                continue
            if _is_mention(msg, user_id):
                hits.append(MentionHit(channel_id=scope_channel_id, message=msg))
                if len(hits) >= safe_limit:
                    return hits
    return hits
