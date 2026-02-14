from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from discord_reader.client import DiscordClient
from discord_reader.models import MentionHit
from discord_reader.search import search_mentions


@dataclass
class Favorite:
    target_id: str
    kind: str
    label: str | None = None


class InboxStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS favorites (
                target_id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                label TEXT
            );
            CREATE TABLE IF NOT EXISTS read_state (
                target_id TEXT PRIMARY KEY,
                last_read_message_id TEXT
            );
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS favorite_tags (
                target_id TEXT NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (target_id, tag_id),
                FOREIGN KEY (target_id) REFERENCES favorites(target_id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

    def add_favorite(
        self, target_id: str, kind: str = "channel", label: str | None = None
    ) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO favorites(target_id, kind, label) VALUES (?, ?, ?)",
            (target_id, kind, label),
        )
        self.conn.commit()

    def remove_favorite(self, target_id: str) -> None:
        self.conn.execute("DELETE FROM favorites WHERE target_id=?", (target_id,))
        self.conn.commit()

    def list_favorites(self) -> list[Favorite]:
        rows = self.conn.execute(
            "SELECT target_id, kind, label FROM favorites ORDER BY target_id"
        ).fetchall()
        return [Favorite(**dict(row)) for row in rows]

    def mark_read(self, target_id: str, message_id: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO read_state(target_id, last_read_message_id) VALUES (?, ?)",
            (target_id, message_id),
        )
        self.conn.commit()

    def get_last_read(self, target_id: str) -> str | None:
        row = self.conn.execute(
            "SELECT last_read_message_id FROM read_state WHERE target_id=?",
            (target_id,),
        ).fetchone()
        return None if row is None else row[0]

    def add_tag(self, name: str) -> None:
        self.conn.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (name,))
        self.conn.commit()

    def tag_favorite(self, target_id: str, tag_name: str) -> None:
        self.add_tag(tag_name)
        row = self.conn.execute(
            "SELECT id FROM tags WHERE name=?", (tag_name,)
        ).fetchone()
        self.conn.execute(
            "INSERT OR IGNORE INTO favorite_tags(target_id, tag_id) VALUES (?, ?)",
            (target_id, row[0]),
        )
        self.conn.commit()


def mentions_across_favorites(
    client: DiscordClient, store: InboxStore, user_id: str, limit: int = 100
) -> list[MentionHit]:
    hits: list[MentionHit] = []
    for favorite in store.list_favorites():
        if favorite.kind != "channel":
            continue
        channel_hits = search_mentions(
            client, user_id=user_id, channel_id=favorite.target_id, limit=limit
        )
        hits.extend(channel_hits)
        if len(hits) >= limit:
            break
    return hits[:limit]
