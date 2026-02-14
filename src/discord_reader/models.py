from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str
    username: str | None = None
    global_name: str | None = None


class Guild(BaseModel):
    id: str
    name: str


class Channel(BaseModel):
    id: str
    guild_id: str | None = None
    parent_id: str | None = None
    type: int
    name: str | None = None
    topic: str | None = None
    nsfw: bool | None = None
    position: int | None = None


class Attachment(BaseModel):
    id: str
    filename: str
    url: str | None = None


class Message(BaseModel):
    id: str
    channel_id: str
    author: User
    timestamp: datetime
    content: str = ""
    mentions: list[User] = Field(default_factory=list)
    attachments: list[Attachment] = Field(default_factory=list)


class MentionHit(BaseModel):
    guild_id: str | None = None
    guild_name: str | None = None
    channel_id: str
    channel_name: str | None = None
    message: Message

    @property
    def jump_url(self) -> str:
        guild_part = self.guild_id or "@me"
        return f"https://discord.com/channels/{guild_part}/{self.channel_id}/{self.message.id}"
