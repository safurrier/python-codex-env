from __future__ import annotations

from discord_reader.client import DiscordClient
from discord_reader.models import Guild


def list_guilds(client: DiscordClient) -> list[Guild]:
    data = client.get("users/@me/guilds")
    return [Guild.model_validate(item) for item in data]


def get_guild(client: DiscordClient, guild_id: str) -> Guild:
    data = client.get(f"guilds/{guild_id}")
    return Guild.model_validate(data)
