from __future__ import annotations

from discord_reader.client import DiscordClient
from discord_reader.models import Channel


def list_guild_channels(client: DiscordClient, guild_id: str) -> list[Channel]:
    data = client.get(f"guilds/{guild_id}/channels")
    return [Channel.model_validate(item) for item in data]


def get_channel(client: DiscordClient, channel_id: str) -> Channel:
    data = client.get(f"channels/{channel_id}")
    return Channel.model_validate(data)
