from __future__ import annotations

from datetime import datetime, timedelta, timezone

from discord_reader.channels import list_guild_channels
from discord_reader.client import DiscordAPIError, DiscordClient
from discord_reader.messages import list_messages
from discord_reader.models import MentionHit, Message


def _is_mention(message: Message, user_id: str) -> bool:
    if any(user.id == user_id for user in message.mentions):
        return True
    return f"<@{user_id}>" in message.content or f"<@!{user_id}>" in message.content


def _parse_since(*, since: str | None, last: int | None) -> datetime | None:
    if since:
        return datetime.fromisoformat(since.replace("Z", "+00:00"))
    if last is None:
        return None
    return datetime.now(tz=timezone.utc) - timedelta(days=last)


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
    since_dt = _parse_since(since=since, last=last)
    scopes = [channel_id] if channel_id else []
    if guild_id and not scopes:
        scopes = [c.id for c in list_guild_channels(client, guild_id)]

    hits: list[MentionHit] = []
    if channel_id:
        search_path = f"channels/{channel_id}/messages/search"
    elif guild_id:
        search_path = f"guilds/{guild_id}/messages/search"
    else:
        search_path = None

    if search_path:
        try:
            search_data = client.get(
                search_path,
                params={"mentions": user_id, "limit": limit},
                allow_202_retry=True,
            )
            for group in search_data.get("messages", []):
                for raw_msg in group:
                    msg = Message.model_validate(raw_msg)
                    if since_dt and msg.timestamp < since_dt:
                        continue
                    hits.append(MentionHit(channel_id=msg.channel_id, message=msg))
            return hits
        except DiscordAPIError as exc:
            if not any(code in str(exc) for code in ["403", "404", "501"]):
                raise

    if not scopes and not channel_id and not guild_id:
        raise DiscordAPIError("Mentions fallback requires --guild or --channel scope")

    for scope_channel_id in scopes:
        for msg in list_messages(client, scope_channel_id, limit=min(limit, 100)):
            if since_dt and msg.timestamp < since_dt:
                continue
            if _is_mention(msg, user_id):
                hits.append(MentionHit(channel_id=scope_channel_id, message=msg))
                if len(hits) >= limit:
                    return hits
    return hits
